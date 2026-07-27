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

| Service | Purpose | Security & Operations Enhancements |
|---|---|---|
| **AWS IoT Core** | Receives MQTT sensor data | Least-privilege IoT Device Policy (restricted client & topics) |
| **AWS Lambda** | Runs anomaly detection logic | Dedicated CloudWatch Log Group with 30-day retention, structured JSON logging |
| **AWS SNS** | Sends email & SMS alerts | KMS Server-Side Encryption (using `alias/aws/sns`) |
| **AWS DynamoDB** | Stores all readings + anomaly flags | KMS Server-Side Encryption, PITR enabled, 30-day Auto-cleanup TTL |
| **AWS CloudWatch** | Monitors Lambda, sets alarms | Configured Metric Alarm on errors routing to SNS topic |
| **AWS IAM** | Roles and permissions | Least-privilege role targeting specific Log Group ARN |

---

## 📁 Project Structure

```
iot-anomaly-detection/
│
├── .github/
│   └── workflows/
│       ├── ci.yml             # GitHub Actions CI pipeline (lint, validate, test)
│       └── security.yml       # GitHub Actions Security scanner (bandit, tfsec)
│
├── device-simulator/
│   ├── sensor_publisher.py    # Sends sensor data (with random anomalies)
│   ├── config.py              # AWS IoT config (loads from env variables)
│   ├── requirements.txt       # Pins dependency versions + testing tools
│   ├── Dockerfile             # Multi-stage lightweight Docker image
│   ├── .dockerignore          # Context exclusions (excludes certs, test files)
│   └── tests/
│       └── test_publisher.py  # Unit testing suite for publisher
│
├── lambda/
│   ├── lambda_function.py     # Refactored anomaly detection (structured JSON logs)
│   ├── requirements.txt       # Development dependencies for testing
│   └── test_lambda_function.py # Unit testing suite for Lambda function
│
├── terraform/                 # Infrastructure as Code (IaC)
│   ├── provider.tf            # AWS & S3 backend templates
│   ├── variables.tf           # Config variables with type & format validations
│   ├── dynamodb.tf            # Encrypted DynamoDB Table with TTL configuration
│   ├── logs.tf                # Dedicated CloudWatch Log Group
│   ├── sns.tf                 # Encrypted SNS Alert Topic
│   ├── iam.tf                 # Least-privilege role configurations
│   ├── lambda.tf              # Lambda provisioning & code archiving
│   ├── iot.tf                 # IoT Core Rule & Restricted Device Policy
│   ├── monitoring.tf          # CloudWatch error alarm
│   └── outputs.tf             # Output values (endpoint, ARNs)
│
├── docs/
│   └── devops_runbook.md      # DevOps operational runbook & incident guides
│
├── docker-compose.yml         # Compose config for running simulator locally
└── .pre-commit-config.yaml    # Pre-commit hook validations (black, flake8, tf fmt)
```

---

## 🚨 Anomaly Rules

| Sensor | Normal Range | Anomaly Threshold | Environment Config Variable |
|---|---|---|---|
| Temperature | 15°C – 35°C | < 10°C or > 40°C | `THRESHOLD_TEMP_MIN` / `THRESHOLD_TEMP_MAX` |
| Humidity | 20% – 80% | < 15% or > 90% | `THRESHOLD_HUMI_MIN` / `THRESHOLD_HUMI_MAX` |
| Pressure | 980 – 1050 hPa | < 950 or > 1080 hPa | `THRESHOLD_PRESS_MIN` / `THRESHOLD_PRESS_MAX` |

*Thresholds can be customized dynamically using Lambda environment variables without code redeployments.*

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

Once deployed, copy the output parameters (`iot_endpoint`, `sns_topic_arn`, etc.) to configure your simulator environment variables.

### Step 2 — Run Sensor Publisher
You can run the publisher locally or inside a Docker container.

#### Option A: Running with Docker Compose (Recommended)
Make sure you put your AWS IoT certificates under `device-simulator/certs/` first, then run:
```bash
# Update environment variables inside docker-compose.yml first
docker-compose up --build -d
```

#### Option B: Running Locally
```bash
cd device-simulator
pip install -r requirements.txt
# Add certs to device-simulator/certs/
# Setup configurations in config.py or set environment variables:
# export AWS_IOT_ENDPOINT="your-endpoint.iot.us-east-1.amazonaws.com"
python sensor_publisher.py
```

### Step 3 — Run Tests Locally
You can run python unit tests locally for validation:

* **Lambda Tests:**
  ```bash
  pip install -r lambda/requirements.txt
  pytest lambda/test_lambda_function.py -v
  ```

* **Simulator Tests:**
  ```bash
  pip install -r device-simulator/requirements.txt
  pytest device-simulator/test_publisher.py -v
  ```

---

## ⚙️ CI/CD & Local Code Quality

### GitHub Actions Pipelines
1. **CI Pipeline** (`.github/workflows/ci.yml`): Triggered on push or PR to `main`. Checks python code formatting (Black), lints (Flake8), runs pytest unit tests for both lambda and simulator, and validates Terraform code syntax (`terraform validate` and `terraform fmt`).
2. **Security Pipeline** (`.github/workflows/security.yml`): Runs `bandit` to identify python code security flaws and `tfsec` to check Terraform template security weaknesses.

### Local Pre-commit Hooks
Install pre-commit hooks to validate code quality before commits:
```bash
pip install pre-commit
pre-commit install
```
This runs generic formatting checks, `black`, `flake8`, and `terraform fmt` checks automatically on git commit.

---

## 📖 Operational Guide
For advanced queries, metrics monitoring setup, disaster recovery policies, and incident playbooks, refer to the [DevOps Operations Runbook](file:///c:/Users/User/Desktop/IOT%20ANOMALITY/docs/devops_runbook.md).

---

## 👤 Author

**Melvin Chacko Jose**
- Email: melvinjose025@gmail.com

---

## 📄 License
MIT License
