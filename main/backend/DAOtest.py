import os
os.add_dll_directory("C:/Users/bjones2/Downloads/Capstone-Final/NextGen-Finale/myvenv/Lib/site-packages/clidriver/bin")
 
clidriver_path = "C:/Users/bjones2/Downloads/Capstone-Final/NextGen-Finale/myvenv/Lib/site-packages/clidriver/bin/amd64.VC12.CRT"

os.environ["PATH"] = clidriver_path + ";" + os.environ.get("PATH", "")
 
import ibm_db

from pathlib import Path
import sys, ibm_db

pkg_root = Path(ibm_db.__file__).parent
clidriver = pkg_root / "clidriver"
license_dir = clidriver / "license"

if license_dir.exists():
    print("license files:", [p.name for p in license_dir.glob("*.lic")])

conn_str = (
    "DATABASE=HL02HL2D;"
    "HOSTNAME=192.168.54.250;"
    "PORT=3600;"
    "PROTOCOL=TCPIP;"
    "AUTHENTICATION=SERVER;"
    "UID=USER02;"
    "PWD=Axon314!;"
)
 
try:
    conn = ibm_db.connect(conn_str,"", "")
except Exception as e:
    print("SQLSTATE:", ibm_db.conn_error())
    print("Message :", ibm_db.conn_errormsg())
    conn=None
 
if conn:
    ibm_db.close(conn)