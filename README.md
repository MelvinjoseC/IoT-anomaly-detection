# 🚨 IoT Anomaly Detection System — AWS Cloud

An intelligent IoT monitoring system that detects **sensor anomalies** in real-time and sends instant **email/SMS alerts** using AWS SNS — before problems become failures.

---

## 📐 Architecture

```
[ESP32 / Raspberry Pi]
  Sensor Data
  (Temperature, Humidity, Pressure)
        |
        | MQTT (port 8883)
        ↓
[AWS IoT Core]
        |
        | IoT Rule → Lambda
        ↓
[AWS Lambda]
  Anomaly Detection Logic
        |
        ├── Normal → Store to DynamoDB
        │
        └── Anomaly Detected!
              |
              ↓
         [AWS SNS]
              |
              ├── 📧 Email Alert
              └── 📱 SMS Alert

[CloudWatch Alarms] ← monitors Lambda errors
```

---

## 🛠️ AWS Services Used

| Service | Purpose |
|---|---|
| AWS IoT Core | Receives MQTT sensor data |
| AWS Lambda | Runs anomaly detection logic |
| AWS SNS | Sends email & SMS alerts |
| AWS DynamoDB | Stores all readings + anomaly flags |
| AWS CloudWatch | Monitors Lambda, sets alarms |
| AWS IAM | Roles and permissions |

---

## 📁 Project Structure

```
iot-anomaly-detection/
│
├── device-simulator/
│   ├── sensor_publisher.py    # Sends sensor data (with random anomalies)
│   ├── config.py              # AWS IoT config
│   ├── requirements.txt
│   └── certs/                 # AWS IoT certificates
│
├── lambda/
│   ├── lambda_function.py     # Anomaly detection + SNS alerts
│   └── requirements.txt
│
├── infrastructure/
│   └── aws_setup_guide.md     # Step-by-step AWS setup
│
└── docs/
    └── architecture.md
```

---

## 🚨 Anomaly Rules

| Sensor | Normal Range | Anomaly Threshold |
|---|---|---|
| Temperature | 15°C – 35°C | < 10°C or > 40°C |
| Humidity | 20% – 80% | < 15% or > 90% |
| Pressure | 980 – 1050 hPa | < 950 or > 1080 hPa |

When **any threshold is crossed**, an alert fires instantly.

---

## 📊 Alert Example

```
🚨 ANOMALY ALERT — IoT Sensor System

Device    : RaspberryPi-Sensor-01
Timestamp : 2024-01-15T10:30:00Z
Anomaly   : HIGH TEMPERATURE DETECTED
Value     : 45.2°C (threshold: 40°C)
Action    : Immediate inspection required
```

---

## 🚀 Quick Start

### Step 1 — Set up AWS
```
Follow infrastructure/aws_setup_guide.md
```

### Step 2 — Run Sensor Publisher
```bash
cd device-simulator
pip install -r requirements.txt
# Add certs to device-simulator/certs/
# Edit config.py
python sensor_publisher.py
```

### Step 3 — Check Alerts
- Email: Check subscribed email inbox
- SMS: Check subscribed phone number
- DynamoDB: See all readings with anomaly flags

---

## 👤 Author

**Melvin Chacko Jose**
- GitHub: [github.com/YOUR_USERNAME](https://github.com)
- LinkedIn: [linkedin.com/in/YOUR_PROFILE](https://linkedin.com)
- Email: melvinjose025@gmail.com

---

## 📄 License
MIT License
