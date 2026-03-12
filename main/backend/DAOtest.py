import os
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.utilities.logger import LoggerFactory

# Set up IBM DB2 connection through the virtual environment
# Dynamically find the clidriver paths in the virtual environment
venv_path = project_root / "myvenv" / "Lib" / "site-packages" / "clidriver"
clidriver_bin = venv_path / "bin"
clidriver_crt = clidriver_bin / "amd64.VC12.CRT"

# Add the bin directory to DLL search path
os.add_dll_directory(str(clidriver_bin))
# Add CRT directory to PATH environment variable
os.environ["PATH"] = str(clidriver_crt) + ";" + os.environ.get("PATH", "")
import ibm_db

# Load credentials from JSON file
credentials_path = Path(__file__).parent.parent.parent / "credentials.json"
with open(credentials_path, "r") as f:
    credentials = json.load(f)

# Build connection string dynamically
conn_str = (
    f"DATABASE={credentials['database']};"
    f"HOSTNAME={credentials['hostname']};"
    f"PORT={credentials['port']};"
    f"PROTOCOL={credentials['protocol']};"
    f"AUTHENTICATION={credentials['authentication']};"
    f"UID={credentials['uid']};"
    f"PWD={credentials['pwd']};"
)
 
try:
    conn = ibm_db.connect(conn_str,"", "")
except Exception as e:
    print("SQLSTATE:", ibm_db.conn_error())
    print("Message :", ibm_db.conn_errormsg())
    conn=None
 
if conn:
    print("SUCCESS: Connection to database established.")
    
    # Create a DBI connection for easier database operations
    import ibm_db_dbi
    dbi_conn = ibm_db_dbi.Connection(conn)
    cursor = dbi_conn.cursor()
    logger = LoggerFactory.get_general_logger()
    
    try:
        # Check if table already exists by trying to select from it
        print("\n--- Checking if table exists ---")
        logger.info("Checking if table exists")
        table_exists = False
        try:
            cursor.execute("SELECT 1 FROM TEST_TABLE FETCH FIRST 1 ROW ONLY")
            cursor.fetchone()
            table_exists = True
            print("Table 'TEST_TABLE' already exists.")
            logger.info("Table 'TEST_TABLE' already exists")
        except Exception as check_error:
            # Table doesn't exist (or other error)
            print("Table does not exist.")
            logger.info("Table does not exist")
        
        # Create table only if it doesn't exist
        if not table_exists:
            print("\n--- Creating test table ---")
            logger.info("Creating test table")
            create_table_sql = """
            CREATE TABLE TEST_TABLE (
                ID INTEGER NOT NULL,
                NAME VARCHAR(50),
                DESCRIPTION VARCHAR(100),
                PRIMARY KEY (ID)
            )
            """
            cursor.execute(create_table_sql)
            print("Table 'TEST_TABLE' created successfully.")
            logger.info("Table 'TEST_TABLE' created successfully")
        
        # Get the actual z/OS dataset name (DSN) for the table
        print("\n--- Table Dataset Information ---")
        logger.info("Retrieving table dataset information")
        try:
            # Query to get the tablespace and dataset information
            cursor.execute("""
                SELECT T.CREATOR, T.NAME, T.TSNAME, TS.DBNAME
                FROM SYSIBM.SYSTABLES T
                LEFT JOIN SYSIBM.SYSTABLESPACE TS ON T.TSNAME = TS.NAME
                WHERE T.NAME = 'TEST_TABLE'
            """)
            table_info = cursor.fetchone()
            
            if table_info:
                creator = table_info[0].strip()
                table_name = table_info[1].strip()
                tablespace = table_info[2].strip() if table_info[2] else 'N/A'
                database = table_info[3].strip() if table_info[3] else 'N/A'
                
                print(f"Creator/Schema: {creator}")
                print(f"Table Name: {table_name}")
                print(f"Tablespace: {tablespace}")
                print(f"Database: {database}")
                print(f"Qualified Table Name: {creator}.{table_name}")
                
                # Try to get the actual dataset name(s) from tablespace
                try:
                    cursor.execute("""
                        SELECT VCATNAME, NAME, DBNAME
                        FROM SYSIBM.SYSTABLESPACE
                        WHERE NAME = ?
                    """, (tablespace,))
                    ts_info = cursor.fetchone()
                    if ts_info:
                        vcat = ts_info[0].strip() if ts_info[0] else 'N/A'
                        ts_name = ts_info[1].strip() if ts_info[1] else 'N/A'
                        db_name = ts_info[2].strip() if ts_info[2] else 'N/A'
                        print(f"\nTablespace Details:")
                        print(f"  VCAT: {vcat}")
                        print(f"  Database.Tablespace: {db_name}.{ts_name}")
                        
                        # The actual DSN pattern is typically: VCAT.DSNDBxxx.DBNAMExx.TSNAMExx.I0001.A001
                        print(f"\nLikely DSN pattern: {vcat}.DSNDB{database[-3:]}.{tablespace}.*.I0001.A001")
                        print(f"Or look for datasets matching: {vcat}.DSNDB*.{tablespace}.*")
                except Exception as ts_error:
                    print(f"\nCould not retrieve tablespace details: {ts_error}")
                
                # Try alternate approach to get dataset info
                try:
                    cursor.execute("""
                        SELECT *
                        FROM SYSIBM.SYSTABLEPART
                        WHERE TSNAME = ?
                    """, (tablespace,))
                    part_info = cursor.fetchall()
                    if part_info:
                        print(f"\nTablespace partition info found ({len(part_info)} partitions)")
                except Exception as part_error:
                    pass
                    
            else:
                print("Could not find table in system catalog")
                
        except Exception as e:
            print(f"Could not retrieve table information: {e}")
            print("Table created as: TEST_TABLE")
        
        # Check if table has data and print it
        print("\n--- Checking table contents ---")
        select_sql = "SELECT * FROM TEST_TABLE"
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        
        if rows:
            print(f"Table has {len(rows)} row(s):")
            print(f"{'ID':<5} {'NAME':<20} {'DESCRIPTION':<30}")
            print("-" * 60)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30}")
        else:
            print("Table is empty - seeding initial data...")
            # Seed data only if table is empty
            seed_data = [
                (1, 'Item One', 'First test item AAAA'),
                (2, 'Item Two', 'Second test item BBBB'),
                (3, 'Item Three', 'Third test item CCCC')
            ]
            insert_sql = "INSERT INTO TEST_TABLE (ID, NAME, DESCRIPTION) VALUES (?, ?, ?)"
            for data in seed_data:
                cursor.execute(insert_sql, data)
            dbi_conn.commit()
            print(f"Seeded {len(seed_data)} rows successfully.")
            
            # Display the seeded data
            cursor.execute(select_sql)
            rows = cursor.fetchall()
            print(f"\n{'ID':<5} {'NAME':<20} {'DESCRIPTION':<30}")
            print("-" * 60)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30}")
        
        # Delete the table
        #print("\n--- Dropping test table ---")
        #drop_table_sql = "DROP TABLE TEST_TABLE"
        #cursor.execute(drop_table_sql)
        #print("Table 'TEST_TABLE' dropped successfully.")
        
    except Exception as e:
        print(f"Error during database operations: {e}")
        dbi_conn.rollback()
    finally:
        cursor.close()
        dbi_conn.close()  # This also closes the underlying ibm_db connection
        print("\n--- Connection closed ---")