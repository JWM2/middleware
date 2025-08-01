# middleware

A lightweight FastAPI-based middleware application that maps network devices to MAC addresses and integrates with FortiAnalyzer Cloud via syslog (CEF format) for quarantine event logging.

---

## 🚀 Features

- Add devices to a local SQLite database
- Query and retrieve MAC addresses by `deviceid`, `source_interface`, and `ip`
- Automatically send CEF-formatted syslog logs to FortiAnalyzer Cloud
- Track the last quarantined MAC address
- Built with FastAPI, SQLite, and Docker

---

## 🔧 API Endpoints

### `POST /add-device`
Add one or more devices to the database.

**Request body (multiple devices):**
```json
{
  "devices": [
    {
      "deviceid": "FG60E101",
      "source_interface": "port1",
      "ip": "192.168.10.1",
      "mac": "AA:BB:CC:DD:EE:FF"
    },
    {
      "deviceid": "FG60E102",
      "source_interface": "port2",
      "ip": "192.168.20.1",
      "mac": "11:22:33:44:55:66"
    }
  ]
}
```

**Curl example:**
```bash
curl -X POST http://localhost:8000/add-device \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "deviceid": "FG60E101",
        "source_interface": "port1",
        "ip": "192.168.10.1",
        "mac": "AA:BB:CC:DD:EE:FF"
      },
      {
        "deviceid": "FG60E102",
        "source_interface": "port2",
        "ip": "192.168.20.1",
        "mac": "11:22:33:44:55:66"
      }
    ]
  }'
```

---

### `POST /get-and-quarantine`
Look up a MAC address by `deviceid`, `source_interface`, and `ip`. If found, logs a CEF event to FortiAnalyzer.

**Request body:**
```json
{
  "deviceid": "FG60E101",
  "source_interface": "port1",
  "ip": "192.168.10.1"
}
```

**Response:**
```json
{ "mac": "AA:BB:CC:DD:EE:FF" }
```

---

### `GET /last-quarantine`
Returns the last quarantined MAC address.

---

## 🐳 Docker Usage

### Build:

```bash
docker build --platform=linux/amd64 -t middleware-server:v5 .
```

### Run:

```bash
docker run -d -p 8000:8000 --name middleware-app middleware-server:v5
```

### Access:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠 Dependencies

Listed in `requirements.txt`, including:
- fastapi
- uvicorn
- sqlite3
- pydantic

---

## 📂 Files

| File         | Purpose                              |
|--------------|--------------------------------------|
| `main.py`    | FastAPI app with routes and logic    |
| `models.py`  | Pydantic models for request bodies   |
| `database.py`| DB initialization and helpers        |
| `Dockerfile` | Build and run the container          |
| `.gitignore` | Excludes `devices.db` and cache      |

---


### 🧾 CEF Log Format

When a MAC address is found using `/get-and-quarantine`, the app sends a **CEF-formatted syslog event** to FortiAnalyzer Cloud.

**Example CEF message:**

```
CEF:0|MiddlewareCo|QuarantineApp|1.0|1001|MAC quarantine event|5|mac=AA:BB:CC:DD:EE:FF deviceid=FG60E101 srcintf=port1 ip=192.168.10.1
```

**Breakdown:**

| Field          | Meaning                                         |
|----------------|-------------------------------------------------|
| `CEF:0`        | CEF version                                     |
| `MiddlewareCo` | Vendor name                                     |
| `QuarantineApp`| Product name                                    |
| `1.0`          | Product version                                 |
| `1001`         | Event ID                                        |
| `MAC quarantine event` | Event name                             |
| `5`            | Severity (scale 0–10; 5 = Medium)               |
| `mac=...`      | MAC address of quarantined device               |
| `deviceid=...` | Identifier of the firewall or device            |
| `srcintf=...`  | Source interface of the device                  |
| `ip=...`       | IP address used in the lookup                   |

FortiAnalyzer must be configured to accept syslog over UDP on port `514` and recognize CEF format logs.
