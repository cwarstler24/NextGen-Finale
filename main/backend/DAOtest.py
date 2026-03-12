import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.backend.db_pool import get_db_cursor, db_pool
from main.utilities.logger import LoggerFactory

logger = LoggerFactory.get_general_logger()


def test_database_connection():
    """
    Test if we can connect to the database and query basic system info.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with get_db_cursor() as cursor:
            # Try a simple query to verify connection
            cursor.execute("SELECT CURRENT SERVER FROM SYSIBM.SYSDUMMY1")
            server_name = cursor.fetchone()[0].strip()

            cursor.execute("SELECT CURRENT SCHEMA FROM SYSIBM.SYSDUMMY1")
            current_schema = cursor.fetchone()[0].strip()

            cursor.execute("SELECT USER FROM SYSIBM.SYSDUMMY1")
            user = cursor.fetchone()[0].strip()

            print("✓ Database connection successful!")
            print(f"  Server: {server_name}")
            print(f"  User: {user}")
            print(f"  Current Schema: {current_schema}")
            return True

    except (ConnectionError, OSError, RuntimeError) as e:
        print(f"✗ Database connection failed: {e}")
        logger.error(f"Connection test failed: {e}")
        return False


def check_schema_exists(schema_name: str):
    """
    Check if a schema/database exists.

    Args:
        schema_name (str): The schema name to check

    Returns:
        bool: True if schema exists, False otherwise
    """
    try:
        with get_db_cursor() as cursor:
            # Check if schema exists in catalog (z/OS uses SYSIBM.SYSSCHEMAAUTH
            # or we can check SYSTABLES)
            cursor.execute("""
                SELECT DISTINCT CREATOR
                FROM SYSIBM.SYSTABLES
                WHERE CREATOR = ?
                FETCH FIRST 1 ROW ONLY
            """, (schema_name.upper(),))
            result = cursor.fetchone()

            if result:
                print(f"✓ Schema '{schema_name}' exists")
                return True
            print(f"✗ Schema '{schema_name}' not found")

            # Show available schemas
            print("\nAvailable schemas (with tables):")
            cursor.execute("""
                SELECT DISTINCT CREATOR
                FROM SYSIBM.SYSTABLES
                WHERE TYPE IN ('T', 'V')
                ORDER BY CREATOR
                FETCH FIRST 30 ROWS ONLY
            """)
            schemas = cursor.fetchall()
            for s in schemas:
                print(f"  - {s[0].strip()}")

            return False

    except (ConnectionError, OSError, RuntimeError) as e:
        print(f"✗ Error checking schema: {e}")
        logger.error(f"Schema check failed: {e}")
        return False


def check_table_exists(schema_name: str, table_to_check: str):
    """
    Check if a table exists in the specified schema.

    Args:
        schema_name (str): The schema name (can be empty to search all schemas)
        table_to_check (str): The table name

    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        with get_db_cursor() as cursor:
            # Check if table exists
            if schema_name:
                cursor.execute("""
                    SELECT NAME, CREATOR, TYPE, COLCOUNT
                    FROM SYSIBM.SYSTABLES
                    WHERE CREATOR = ? AND NAME = ?
                """, (schema_name.upper(), table_to_check.upper()))
            else:
                # Search all schemas
                cursor.execute("""
                    SELECT NAME, CREATOR, TYPE, COLCOUNT
                    FROM SYSIBM.SYSTABLES
                    WHERE NAME = ?
                """, (table_to_check.upper(),))

            result = cursor.fetchone()

            if result:
                name = result[0].strip()
                creator = result[1].strip()
                table_type = result[2].strip()
                col_count = result[3]

                print(f"✓ Table '{creator}.{name}' exists")
                print(f"  Type: {table_type}")
                print(f"  Columns: {col_count}")
                return True
            if schema_name:
                print(f"✗ Table '{schema_name}.{table_to_check}' not found")
            else:
                print(f"✗ Table '{table_to_check}' not found in any schema")

            # Show available tables
            if schema_name:
                print(f"\nAvailable tables in schema '{schema_name}':")
                cursor.execute("""
                    SELECT NAME, TYPE, COLCOUNT
                    FROM SYSIBM.SYSTABLES
                    WHERE CREATOR = ? AND TYPE IN ('T', 'V')
                    ORDER BY NAME
                    FETCH FIRST 30 ROWS ONLY
                """, (schema_name.upper(),))
            else:
                print(
                    f"\nTables matching '{table_to_check[:3]}%' in any schema:")
                cursor.execute("""
                    SELECT CREATOR, NAME, TYPE, COLCOUNT
                    FROM SYSIBM.SYSTABLES
                    WHERE NAME LIKE ? AND TYPE IN ('T', 'V')
                    ORDER BY CREATOR, NAME
                    FETCH FIRST 30 ROWS ONLY
                """, (table_to_check[:3].upper() + '%',))

            tables = cursor.fetchall()

            if tables:
                for t in tables:
                    if schema_name:
                        t_name = t[0].strip()
                        t_type = t[1].strip()
                        t_cols = t[2]
                        print(f"  - {t_name} ({t_type}, {t_cols} columns)")
                    else:
                        t_creator = t[0].strip()
                        t_name = t[1].strip()
                        t_type = t[2].strip()
                        t_cols = t[3]
                        print(
                            f"  - {t_creator}.{t_name} ({t_type}, {t_cols} columns)")
            else:
                if schema_name:
                    print(f"  (No tables found in schema '{schema_name}')")
                else:
                    print("  (No tables found)")

            return False

    except (ConnectionError, OSError, RuntimeError) as e:
        print(f"✗ Error checking table: {e}")
        logger.error(f"Table check failed: {e}")
        return False


def query_table(schema_name: str, table_name_to_query: str):
    """
    Query and display all rows from a specified table.

    Args:
        schema_name (str): The database schema name
        table_name_to_query (str): The table name to query
    """
    try:
        with get_db_cursor() as cursor:
            # Construct the fully qualified table name
            qualified_table = f"{schema_name}.{table_name_to_query}" if schema_name else table_name_to_query

            logger.info(
                f"\n--- Querying table: {qualified_table} ---",
                also_print=True)

            # Query all rows from the table
            select_sql = f"SELECT * FROM {qualified_table}"
            cursor.execute(select_sql)
            rows = cursor.fetchall()

            if not rows:
                print(
                    f"\n✓ Query successful - Table '{qualified_table}' is empty (0 rows).")
                return

            # Get column information
            columns = [desc[0] for desc in cursor.description]

            # Print table header
            print("\n✓ Query successful")
            print(f"Table: {qualified_table}")
            print(f"Total rows: {len(rows)}\n")

            # Calculate column widths
            col_widths = []
            for i, col_name in enumerate(columns):
                max_width = len(col_name)
                for row in rows:
                    cell_value = str(row[i]) if row[i] is not None else 'NULL'
                    max_width = max(max_width, len(cell_value))
                col_widths.append(min(max_width, 50))  # Cap at 50 chars

            # Print column headers
            header = " | ".join([col.ljust(col_widths[i])
                                for i, col in enumerate(columns)])
            print(header)
            print("-" * len(header))

            # Print rows
            for row in rows:
                row_str = " | ".join([
                    str(row[i]).ljust(col_widths[i]) if row[i] is not None else 'NULL'.ljust(col_widths[i])
                    for i in range(len(columns))
                ])
                print(row_str)

            print("\n--- Query completed successfully ---")

    except (ConnectionError, OSError, RuntimeError) as e:
        qualified_table = f"{schema_name}.{table_name_to_query}" if schema_name else table_name_to_query
        print(f"\n✗ Error querying table '{qualified_table}': {e}")
        logger.error(f"Query failed: {e}")
        raise


if __name__ == "__main__":
    """
    Interactive DB2 table viewer.
    Prompts user for schema and table name, then displays table contents.
    """
    print("=" * 60)
    print("=== DB2 Table Viewer ===")
    print("=" * 60)
    print(f"Connection pool status: {db_pool.get_pool_status()}\n")

    try:
        # Step 1: Test database connection
        print("STEP 1: Testing database connection...")
        print("-" * 60)
        if not test_database_connection():
            print("\nCannot proceed without database connection.")
            sys.exit(1)

        print("\n" + "=" * 60)

        # Prompt for schema/database
        schema = input(
            "\nEnter the schema/database name (e.g., USER02) or press Enter to skip: ").strip().upper()

        # Step 2: Check if schema exists (only if provided)
        if schema:
            print(f"\nSTEP 2: Checking if schema '{schema}' exists...")
            print("-" * 60)
            if not check_schema_exists(schema):
                response = input(
                    f"\nSchema '{schema}' not verified. Continue anyway? (y/n): ").strip().lower()
                if response != 'y':
                    print("Exiting.")
                    sys.exit(1)
        else:
            print("\nSTEP 2: Schema check skipped (no schema provided)")
            print("-" * 60)

        print("\n" + "=" * 60)

        # Prompt for table name
        table_name = input(
            "\nEnter the table name (e.g., CUSTOMER): ").strip().upper()

        if not table_name:
            print("Error: Table name cannot be empty.")
            sys.exit(1)

        # Step 3: Check if table exists
        print(
            f"\nSTEP 3: Checking if table '{
                schema +
                '.' if schema else ''}{table_name}' exists...")
        print("-" * 60)

        if not check_table_exists(schema, table_name):
            response = input(
                "\nTable not verified. Attempt query anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("Exiting.")
                sys.exit(1)

        print("\n" + "=" * 60)

        # Step 4: Query and display the table
        qualified_name = f"{schema}.{table_name}" if schema else table_name
        print(f"\nSTEP 4: Querying table '{qualified_name}'...")
        print("-" * 60)
        query_table(schema, table_name)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except (ConnectionError, OSError, RuntimeError) as e:
        print(f"\n✗ Failed to query table: {e}")
    finally:
        # Show final pool status
        print("\n" + "=" * 60)
        print(f"Final pool status: {db_pool.get_pool_status()}")
        print("=" * 60)
