from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import logging
import logging.handlers
import socket

app = FastAPI()

# --------- Models ---------
class DeviceQuery(BaseModel):
    deviceid: str
    source_interface: str
    ip: str

class BulkDevice(BaseModel):
    devices: list[dict]

# --------- Database Initialization ---------
def init_db():
    conn = sqlite3.connect("devices.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deviceid TEXT,
            source_interface TEXT,
            ip TEXT,
            mac TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --------- Syslog (CEF) Logging ---------
def send_syslog_to_faz(device_id, source_interface, ip, mac):
    cef_log = (
        "CEF:0|MiddlewareCo|QuarantineApp|1.0|1001|MAC quarantine event|5|"
        f"mac={mac} deviceid={device_id} srcintf={source_interface} ip={ip}"
    )

    logger = logging.getLogger('CEFLogger')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.SysLogHandler(
        address=('1700642.us-east-1.fortianalyzer.forticloud.com', 514),
        socktype=socket.SOCK_DGRAM
    )
    logger.addHandler(handler)

    logger.info(cef_log)

# --------- In-Memory Tracker ---------
last_quarantine = {"mac": None}

# --------- API Endpoints ---------

@app.post("/get-and-quarantine")
def get_and_quarantine(query: DeviceQuery):
    conn = sqlite3.connect("devices.db")
    c = conn.cursor()
    c.execute('''
        SELECT mac FROM devices
        WHERE deviceid=? AND source_interface=? AND ip=?
    ''', (query.deviceid, query.source_interface, query.ip))
    result = c.fetchone()
    conn.close()

    if result:
        mac = result[0]
        last_quarantine["mac"] = mac
        print(f"Told NAC to quarantine {mac}")
        send_syslog_to_faz(query.deviceid, query.source_interface, query.ip, mac)
        return {"mac": mac}
    else:
        raise HTTPException(status_code=404, detail="MAC not found")

@app.post("/add-device")
def add_device(devices: BulkDevice):
    conn = sqlite3.connect("devices.db")
    c = conn.cursor()
    for d in devices.devices:
        c.execute('''
            INSERT INTO devices (deviceid, source_interface, ip, mac)
            VALUES (?, ?, ?, ?)
        ''', (d["deviceid"], d["source_interface"], d["ip"], d["mac"]))
    conn.commit()
    conn.close()
    return {"status": "Devices added"}

@app.get("/last-quarantine")
def last_quarantined():
    if last_quarantine["mac"]:
        return {"last_quarantined_mac": last_quarantine["mac"]}
    else:
        return {"message": "No quarantine has occurred yet"}
