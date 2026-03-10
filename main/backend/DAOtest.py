import os
os.add_dll_directory(r"C:\Users\bjones2\Downloads\Capstone-Final\NextGen-Finale\cs-backend-venv\Lib\site-packages\clidriver\bin")
 
clidriver_path = r"C:\Users\bjones2\Downloads\Capstone-Final\NextGen-Finale\cs-backend-venv\Lib\site-packages\clidriver\bin\amd64.VC12.CRT"
clilicense_path = r"C:\Users\bjones2\Downloads\Capstone-Final\NextGen-Finale\cs-backend-venv\Lib\site-packages\clidriver\license\db2consv_ee.lic"
os.environ["PATH"] = clidriver_path + ";" + clilicense_path + ";" + os.environ.get("PATH", "")
 
import ibm_db
 
conn_str = (
    "AUTHENTICATION=SERVER;"
    "DATABASE=HL02HL2D;"
    "HOSTNAME=192.168.54.250;"
    "PORT=3600;"
    "PROTOCOL=TCPIP;"
    "UID=User02;"
    "PWD=Axon314!;"
)
 
try:
    conn = ibm_db.connect(conn_str,"","")
except Exception as e:
    print("SQLSTATE:", ibm_db.conn_error())
    print("Message :", ibm_db.conn_errormsg())
    conn=None
 
if conn:
    ibm_db.close(conn)