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

def _configure_windows_db2_client_path() -> None:
    """Configure Windows DLL paths only when running on Windows with clidriver present."""
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    if clidriver_bin.exists():
        os.add_dll_directory(str(clidriver_bin))
    if clidriver_crt.exists():
        os.environ["PATH"] = str(clidriver_crt) + ";" + os.environ.get("PATH", "")


_configure_windows_db2_client_path()

DB_CREDENTIAL_ENV_MAPPING = {
    "database": "DB_DATABASE",
    "hostname": "DB_HOSTNAME",
    "port": "DB_PORT",
    "protocol": "DB_PROTOCOL",
    "authentication": "DB_AUTHENTICATION",
    "uid": "DB_UID",
    "pwd": "DB_PWD",
}

try:
    import ibm_db
    import ibm_db_dbi
except ModuleNotFoundError:
    ibm_db = None
    ibm_db_dbi = None


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
        self._min_connections = 1  # Temporarily reduced for VPN testing
        self._max_connections = 10
        self._current_size = 0
        self._schema = "SKYFAL"
        self._environment = "PRODUCTION"
        self._test_data = {}
        self._pool_initialized = False

    def _ensure_pool_initialized(self):
        """Lazily initialize the pool the first time it is needed."""
        if self._pool_initialized:
            return

        with self._connections_lock:
            if self._pool_initialized:
                return
            self._load_database_setup()
            self._load_credentials()
            self._initialize_pool()
            self._pool_initialized = True

    def _load_database_setup(self):
        """Load database setup configuration from database_setup.json"""
        setup_path = project_root / "database_setup.json"
        config = {}
        if setup_path.exists():
            with open(setup_path, "r", encoding="utf-8") as f:
                config = json.load(f)

        self._environment = os.getenv("DB_ENVIRONMENT", config.get("environment", "PRODUCTION"))
        schemas = config.get("schemas", {})
        self._schema = os.getenv("DB_SCHEMA", schemas.get(self._environment, "TSTFAL"))
        self._test_data = config.get("test_data", {})

        self.logger.info(
            f"Database setup loaded: Environment={self._environment}, Schema={self._schema}"
        )

    def _load_credentials(self):
        """Load database credentials from credentials.json"""
        credentials_path = project_root / "credentials.json"
        credentials = {}

        if credentials_path.exists():
            with open(credentials_path, "r", encoding="utf-8") as f:
                credentials = json.load(f)

        for key, env_var in DB_CREDENTIAL_ENV_MAPPING.items():
            env_value = os.getenv(env_var)
            if env_value:
                credentials[key] = env_value

        missing_keys = [key for key in DB_CREDENTIAL_ENV_MAPPING if not credentials.get(key)]
        if missing_keys:
            missing_env_vars = [DB_CREDENTIAL_ENV_MAPPING[key] for key in missing_keys]
            raise RuntimeError(
                "Database credentials are incomplete. Provide credentials.json or set environment variables: "
                + ", ".join(missing_env_vars)
            )

        self._conn_str = (
            f"DATABASE={credentials['database']};"
            f"HOSTNAME={credentials['hostname']};"
            f"PORT={credentials['port']};"
            f"PROTOCOL={credentials['protocol']};"
            f"AUTHENTICATION={credentials['authentication']};"
            f"UID={credentials['uid']};"
            f"PWD={credentials['pwd']};"
            f"CURRENTSCHEMA={self._schema};"
            f"CONNECTTIMEOUT=5;"  # 5 second connection timeout for faster VPN failure
        )
        self.logger.info("Database credentials loaded successfully")

    def _create_connection(self):
        """Create a new DB2 connection using persistent connection for pooling"""
        if ibm_db is None or ibm_db_dbi is None:
            raise RuntimeError(
                "DB2 driver is not available. Install ibm_db and configure DB2 client libraries.")

        try:
            # Log connection attempt (without credentials)
            self.logger.info(f"Attempting DB2 connection to {self._schema} schema...")
            
            # Use regular connect() - pconnect() has cursor state issues with executemany()
            conn = ibm_db.connect(self._conn_str, "", "")
            self.logger.info("Raw DB2 connection established, wrapping in DBI...")
            
            # Wrap it in ibm_db_dbi for thread-safe operations
            dbi_conn = ibm_db_dbi.Connection(conn)
            self.logger.info("DBI wrapper created successfully")

            # Note: No lock needed here - this is only called from _initialize_pool()
            # which is already protected by _connections_lock in _ensure_pool_initialized()
            self._all_connections.append(dbi_conn)
            self._current_size += 1
            self.logger.info(f"Connection added to tracking list (pool size: {self._current_size})")

            self.logger.info(
                f"Created new DB2 connection (pool size: {self._current_size})")
            return dbi_conn

        except Exception as e:
            error_message = str(e)
            # Check if it's a timeout error
            if "timeout" in error_message.lower() or "timed out" in error_message.lower():
                self.logger.error(
                    f"DB2 connection timeout - check VPN/network connectivity: {e}")
            else:
                self.logger.error(f"Failed to create DB2 connection: {e}")
            # Create error response for connection failure
            ResponseCode("DB_CONNECTION_FAILED", data=str(e))
            raise

    def _initialize_pool(self):
        """Initialize the pool with minimum connections"""
        self.logger.info(
            f"Initializing connection pool with {self._min_connections} connections")
        for i in range(self._min_connections):
            self.logger.info(f"Creating connection {i+1}/{self._min_connections}...")
            conn = self._create_connection()
            self.logger.info(f"Connection {i+1} created, adding to pool queue...")
            self._pool.put(conn)
            self.logger.info(f"Connection {i+1} added to pool queue successfully")
        self.logger.info(f"Connection pool initialized with {self._min_connections} connections")

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
        self._ensure_pool_initialized()

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
                    f"Connection pool exhausted. Max connections ({self._max_connections}) reached. Please return connections to the pool.") from exc

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
            except Exception as e:
                self.logger.error(f"Error returning connection to pool: {e}")
                # Connection might be corrupted, remove it
                self._remove_connection(conn)

    def _remove_connection(self, conn):
        """Remove a connection from the pool permanently"""
        try:
            conn.close()
        except Exception:
            pass

        with self._connections_lock:
            if conn in self._all_connections:
                self._all_connections.remove(conn)
                self._current_size -= 1

        self.logger.info(
            f"Removed connection from pool (pool size: {self._current_size})")

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
        if not self._pool_initialized:
            return

        self.logger.info("Closing all database connections")

        # Close connections in the pool
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Exception:
                pass

        # Close any connections that might be in use
        with self._connections_lock:
            for conn in self._all_connections:
                try:
                    conn.close()
                except Exception:
                    pass
            self._all_connections.clear()
            self._current_size = 0
            self._pool_initialized = False

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
        self._ensure_pool_initialized()

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
