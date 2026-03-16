# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

# backend/db_pool.py
import os
import json
import threading
from pathlib import Path
from queue import Queue, Empty
from contextlib import contextmanager
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.utilities.logger import LoggerFactory
from main.utilities.error_handler import ResponseCode

# Set up IBM DB2 connection through the virtual environment
venv_path = project_root / "venv" / "Lib" / "site-packages" / "clidriver"
clidriver_bin = venv_path / "bin"
clidriver_crt = clidriver_bin / "amd64.VC12.CRT"

os.add_dll_directory(str(clidriver_bin))
os.environ["PATH"] = str(clidriver_crt) + ";" + os.environ.get("PATH", "")

import ibm_db
import ibm_db_dbi


class DB2ConnectionPool:
    """
    Thread-safe connection pool for IBM DB2 using ibm_db_dbi.
    Manages a pool of reusable database connections to avoid the overhead
    of creating new connections for each request.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure only one pool exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DB2ConnectionPool, cls).__new__(cls)
                    cls._instance._initialized = False
        else:
            # Ensure _initialized exists on existing instance
            if not hasattr(cls._instance, '_initialized'):
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the connection pool (only once due to singleton)"""
        # Use getattr with default to avoid AttributeError on first
        # instantiation
        if getattr(self, '_initialized', False):
            return

        self.logger = LoggerFactory.get_general_logger()
        self._initialized = True
        self._pool = Queue()
        self._all_connections = []
        self._connections_lock = threading.Lock()
        self._conn_str = None
        self._min_connections = 2
        self._max_connections = 10
        self._current_size = 0
        self._schema = None
        self._environment = None
        self._test_data = None

        # Load database setup configuration
        self._load_database_setup()

        # Load credentials and build connection string
        self._load_credentials()

        # Create minimum number of connections
        self._initialize_pool()

    def _load_database_setup(self):
        """Load database setup configuration from database_setup.json"""
        setup_path = project_root / "database_setup.json"
        with open(setup_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self._environment = config.get("environment", "PRODUCTION")
        schemas = config.get("schemas", {})
        self._schema = schemas.get(self._environment, "TSTFAL")
        self._test_data = config.get("test_data", {})

        self.logger.info(
            f"Database setup loaded: Environment={self._environment}, Schema={self._schema}"
        )

    def _load_credentials(self):
        """Load database credentials from credentials.json"""
        credentials_path = project_root / "credentials.json"
        with open(credentials_path, "r", encoding="utf-8") as f:
            credentials = json.load(f)

        self._conn_str = (
            f"DATABASE={credentials['database']};"
            f"HOSTNAME={credentials['hostname']};"
            f"PORT={credentials['port']};"
            f"PROTOCOL={credentials['protocol']};"
            f"AUTHENTICATION={credentials['authentication']};"
            f"UID={credentials['uid']};"
            f"PWD={credentials['pwd']};"
            f"CURRENTSCHEMA={self._schema};"
        )
        self.logger.info("Database credentials loaded successfully")

    def _create_connection(self):
        """Create a new DB2 connection"""
        try:
            # Create raw ibm_db connection
            conn = ibm_db.connect(self._conn_str, "", "")
            # Wrap it in ibm_db_dbi for thread-safe operations
            dbi_conn = ibm_db_dbi.Connection(conn)

            with self._connections_lock:
                self._all_connections.append(dbi_conn)
                self._current_size += 1

            self.logger.info(
                f"Created new DB2 connection (pool size: {
                    self._current_size})")
            return dbi_conn

        except Exception as e:
            self.logger.error(f"Failed to create DB2 connection: {e}")
            # Create error response for connection failure
            ResponseCode("DB_CONNECTION_FAILED", data=str(e))
            raise

    def _initialize_pool(self):
        """Initialize the pool with minimum connections"""
        self.logger.info(
            f"Initializing connection pool with {
                self._min_connections} connections")
        for _ in range(self._min_connections):
            conn = self._create_connection()
            self._pool.put(conn)

    def get_connection(self, timeout=5):
        """
        Get a connection from the pool. Creates a new one if pool is empty
        and max connections not reached.

        Args:
            timeout (int): Seconds to wait for a connection from the pool

        Returns:
            ibm_db_dbi.Connection: A database connection

        Raises:
            Exception: If unable to get a connection
        """
        try:
            # Try to get an existing connection from the pool
            conn = self._pool.get(timeout=timeout)
            self.logger.debug("Retrieved connection from pool")
            return conn

        except Empty as exc:
            # Pool is empty, create new connection if under max limit
            with self._connections_lock:
                if self._current_size < self._max_connections:
                    self.logger.info("Pool empty, creating new connection")
                    return self._create_connection()
                # Create error response for pool exhaustion
                ResponseCode(
                    "DB_CONNECTION_POOL_EXHAUSTED",
                    data={
                        "max_connections": self._max_connections,
                        "current_size": self._current_size,
                        "pool_available": self._pool.qsize()
                    }
                )
                raise RuntimeError(
                    f"Connection pool exhausted. Max connections ({
                        self._max_connections}) reached. Please return connections to the pool.") from exc

    def return_connection(self, conn):
        """
        Return a connection to the pool for reuse.

        Args:
            conn (ibm_db_dbi.Connection): The connection to return
        """
        if conn:
            try:
                # Rollback any uncommitted transactions
                conn.rollback()
                self._pool.put(conn)
                self.logger.debug("Connection returned to pool")
            except (ibm_db.DatabaseError, ValueError) as e:
                self.logger.error(f"Error returning connection to pool: {e}")
                # Connection might be corrupted, remove it
                self._remove_connection(conn)

    def _remove_connection(self, conn):
        """Remove a connection from the pool permanently"""
        try:
            conn.close()
        except (ibm_db.DatabaseError, AttributeError):
            pass

        with self._connections_lock:
            if conn in self._all_connections:
                self._all_connections.remove(conn)
                self._current_size -= 1

        self.logger.info(
            f"Removed connection from pool (pool size: {
                self._current_size})")

    @contextmanager
    def get_cursor(self):
        """
        Context manager for getting a cursor. Automatically handles
        connection acquisition and return.

        Usage:
            with pool.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                rows = cursor.fetchall()
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            yield cursor
            conn.commit()  # Auto-commit on success
        except Exception as e:
            if conn:
                conn.rollback()  # Rollback on error
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    def close_all(self):
        """Close all connections in the pool. Should be called on application shutdown."""
        self.logger.info("Closing all database connections")

        # Close connections in the pool
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except (ibm_db.DatabaseError, AttributeError):
                pass

        # Close any connections that might be in use
        with self._connections_lock:
            for conn in self._all_connections:
                try:
                    conn.close()
                except (ibm_db.DatabaseError, AttributeError):
                    pass
            self._all_connections.clear()
            self._current_size = 0

        self.logger.info("All database connections closed")

    def get_pool_status(self):
        """Get current pool statistics"""
        return {
            "pool_size": self._pool.qsize(),
            "total_connections": self._current_size,
            "max_connections": self._max_connections,
            "min_connections": self._min_connections
        }

    def get_environment(self):
        """Get the current database environment (PRODUCTION or TEST)"""
        return self._environment

    def get_schema(self):
        """Get the current database schema name"""
        return self._schema

    def is_test_environment(self):
        """Check if running in TEST environment"""
        return self._environment == "TEST"

    def get_test_data(self, table_name=None):
        """
        Get test data for populating tables.

        Args:
            table_name (str, optional): Specific table name. If None, returns all test data.

        Returns:
            dict or list: Test data for the specified table or all test data
        """
        if table_name:
            return self._test_data.get(table_name, [])
        return self._test_data

    def populate_test_data(self):
        """
        Populate all tables with test data. Should only be used in TEST environment.

        Returns:
            dict: Status of population operation with counts per table
        """
        if not self.is_test_environment():
            self.logger.warning(
                "Attempted to populate test data in non-TEST environment. Operation blocked."
            )
            return {"status": "blocked", "reason": "Not in TEST environment"}

        self.logger.info("Starting test data population...")
        results = {}

        with self.get_cursor() as cursor:
            for table_name, rows in self._test_data.items():
                if not rows:
                    results[table_name] = {"inserted": 0, "status": "empty"}
                    continue

                try:
                    # Clear existing data
                    cursor.execute(f"DELETE FROM {self._schema}.{table_name}")

                    # Insert test data
                    inserted_count = 0
                    for row in rows:
                        columns = ", ".join(row.keys())
                        placeholders = ", ".join(["?" for _ in row])
                        sql = f"INSERT INTO {self._schema}.{table_name} ({columns}) VALUES ({placeholders})"
                        cursor.execute(sql, list(row.values()))
                        inserted_count += 1

                    results[table_name] = {
                        "inserted": inserted_count,
                        "status": "success"
                    }
                    self.logger.info(
                        f"Populated {table_name} with {inserted_count} rows"
                    )

                except Exception as e:
                    results[table_name] = {
                        "inserted": 0,
                        "status": "error",
                        "error": str(e)
                    }
                    self.logger.error(
                        f"Failed to populate {table_name}: {e}"
                    )

        self.logger.info("Test data population completed")
        return results


# Global pool instance (singleton)
db_pool = DB2ConnectionPool()


# Convenience function for use in other modules
def get_db_cursor():
    """
    Get a database cursor with automatic connection management.

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            rows = cursor.fetchall()
    """
    return db_pool.get_cursor()
