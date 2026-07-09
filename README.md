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
├── terraform/                 # Infrastructure as Code (IaC)
│   ├── provider.tf            # AWS & Archive providers
│   ├── variables.tf           # Configuration variables
│   ├── dynamodb.tf            # SensorReadings DynamoDB Table
│   ├── sns.tf                 # SNS Alert Topic & email sub
│   ├── iam.tf                 # Least-privilege roles/policies
│   ├── lambda.tf              # Lambda provisioning & code archiving
│   ├── iot.tf                 # IoT Core Rule & Device Policy
│   ├── monitoring.tf          # CloudWatch error alarm
│   └── outputs.tf             # Output values (endpoint, ARNs)
│
├── infrastructure/
│   └── aws_setup_guide.md     # Step-by-step manual setup
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

### Step 1 — Deploy AWS Infrastructure via Terraform (Recommended)
You can deploy the entire AWS architecture (DynamoDB, SNS, IAM roles, Lambda function, IoT Core rules, policies, and CloudWatch alarms) in minutes:
```bash
cd terraform
terraform init
terraform apply -var="alert_email=your-email@example.com"
```
*Note: Make sure your AWS CLI credentials are configured (`aws configure`).*

Once deployed, copy the output parameters (`iot_endpoint`, `sns_topic_arn`, etc.) to update your `device-simulator/config.py`.

*Alternatively, see [infrastructure/aws_setup_guide.md](file:///c:/Users/User/Desktop/IoT-anomaly-detection/infrastructure/aws_setup_guide.md) for manual AWS console setup.*

### Step 2 — Run Sensor Publisher
```bash
cd device-simulator
pip install -r requirements.txt
# Add certs to device-simulator/certs/ (see Step 5 of manual setup)
# Edit config.py (add endpoint and certificate names)
python sensor_publisher.py
```

### Step 3 — Check Alerts
- **Email**: Confirm your subscription via the link sent to your alert email address and monitor incoming alert messages.
- **DynamoDB**: Check the `SensorReadings` table to see sensor data along with `is_anomaly` flags.

---

## 👤 Author

**Melvin Chacko Jose**
- Email: melvinjose025@gmail.com

---

## 📄 License
MIT License
