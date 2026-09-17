# 🚨 IoT Anomaly Detection System — Enterprise DevOps & Cloud Platform

[![CI Pipeline](https://github.com/MelvinjoseC/IoT-anomaly-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/MelvinjoseC/IoT-anomaly-detection/actions/workflows/ci.yml)
[![Security Scan](https://github.com/MelvinjoseC/IoT-anomaly-detection/actions/workflows/security.yml/badge.svg)](https://github.com/MelvinjoseC/IoT-anomaly-detection/actions/workflows/security.yml)
[![Terraform](https://img.shields.io/badge/IaC-Terraform_v1.6+-844FBA.svg?logo=terraform)](https://www.terraform.io)
[![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12-3776AB.svg?logo=python)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Hardened_Non--Root-2496ED.svg?logo=docker)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, highly available IoT monitoring platform that ingests real-time telemetry, detects sensor anomalies, and fires instant notifications via AWS SNS — with automated SQS dead-letter failover, distributed AWS X-Ray tracing, and centralized CloudWatch dashboards.

---

## 📐 Production Cloud Architecture

```
┌──────────────────────────────────────┐
│  ESP32 / Raspberry Pi / Simulator    │
│  (Dockerized Non-root / Mock Mode)   │
│  Reads: Temp, Humidity, Pressure     │
└──────────────────┬───────────────────┘
                   │ MQTT over TLS (Port 8883)
                   │ Topic: sensors/environment
                   ▼
┌──────────────────────────────────────┐
│  AWS IoT Core                        │
│  • X.509 mutual authentication       │
│  • Topic Rule: sensors/environment   │
└─────────┬──────────────────┬─────────┘
          │ Invoke           │ Error / Throttle Action
          ▼                  ▼
┌──────────────────┐  ┌──────────────────────────────────────┐
│   AWS Lambda     │  │  AWS SQS Dead-Letter Queue (DLQ)     │
│  (IoTAnomaly-    │  │  • 14-day encrypted retention        │
│   Detector)      │  │  • Alarm on visible messages         │
│  • X-Ray Tracing │  └──────────────────┬───────────────────┘
│  • JSON logging  │                     ▲
└─┬──────────────┬─┘                     │ Asynchronous Redrive
  │              │                       │
  │ Anomaly      │ Always (All Data)     │
  ▼              ▼                       │
┌──────────────┐ ┌─────────────────────────┴────────┐
│   AWS SNS    │ │  AWS DynamoDB (SensorReadings)    │
│  • Encrypted │ │  • PK: device_id, SK: timestamp  │
│  • Email/SMS │ │  • GSI: AnomalyIndex             │
│    alerts    │ │  • TTL Auto-cleanup (30 Days)     │
└──────────────┘ └───────────────────────────────────┘
       ▲                          ▲
       │                          │
┌──────┴──────────────────────────┴─────────────────┐
│  Centralized Observability & Reliability           │
│  • CloudWatch Operational Dashboard as Code       │
│  • Metric Alarms: Errors, Throttles, Latency, DLQ  │
│  • AWS X-Ray Distributed End-to-End Tracing       │
└───────────────────────────────────────────────────┘
```

---

## 🛠️ AWS Services & Enterprise Architecture

| Service | Purpose | Security & Operations Enhancements |
|---|---|---|
| **AWS IoT Core** | Receives MQTT sensor data | Least-privilege IoT Device Policy + SQS Dead-Letter Queue error fallback |
| **AWS Lambda** | Runs anomaly detection logic | Dedicated CloudWatch Log Group, dynamic threshold injection, AWS X-Ray active tracing |
| **AWS SQS** | Dead-letter failover | 14-day retention, SSE-SQS encryption, metric alarm on visible message backlog |
| **AWS SNS** | Sends email & SMS alerts | KMS Server-Side Encryption (using `alias/aws/sns`) |
| **AWS DynamoDB** | Stores all readings + anomaly flags | KMS encryption, PITR, 30-day TTL, `AnomalyIndex` Global Secondary Index (GSI) |
| **AWS CloudWatch** | Monitoring & Alerting | Centralized Dashboard as Code + 4 automated Metric Alarms (Errors, Throttles, Latency, DLQ) |
| **AWS X-Ray** | Distributed Tracing | End-to-end telemetry execution timing, cold starts, and downstream latency |
| **AWS IAM** | Roles and permissions | Least-privilege roles targeting specific resource ARNs |

---

## 📁 Project Structure

```
iot-anomaly-detection/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Modern matrix CI pipeline (Python 3.11/3.12, Black, Flake8, Coverage, Terraform)
│   │   └── security.yml           # Bandit SAST, Checkov IaC, and Trivy filesystem scanner
│   ├── ISSUE_TEMPLATE/            # Bug report & feature request templates
│   ├── pull_request_template.md   # PR verification checklist
│   ├── CODEOWNERS                 # Repository ownership definitions
│   └── dependabot.yml             # Weekly automated dependency maintenance
│
├── device-simulator/
│   ├── sensor_publisher.py        # Telemetry publisher with Mock Mode and signal handling
│   ├── config.py                  # Environment-driven simulator configuration
│   ├── requirements.txt           # Pinned production and testing dependencies
│   ├── Dockerfile                 # Multi-stage, non-root hardened container (UID 10001) with HEALTHCHECK
│   ├── .dockerignore              # Excludes test artifacts, certs, and caches
│   └── test_publisher.py          # 10 unit tests for publisher, mock mode, and anomaly rates
│
├── lambda/
│   ├── lambda_function.py         # Anomaly detector with X-Ray SDK, GSI support, structured JSON logging
│   ├── requirements.txt           # Development dependencies for testing
│   └── test_lambda_function.py    # 13 unit tests for boundary conditions, errors, and indexing
│
├── terraform/                     # Production Infrastructure as Code (IaC)
│   ├── provider.tf                # AWS provider (~> 5.0) and backend templates
│   ├── variables.tf               # Validated configuration inputs
│   ├── terraform.tfvars.example   # Variable values reference file
│   ├── environments/              # Environment-specific parameter files
│   │   ├── dev.tfvars             # Development environment overrides
│   │   └── prod.tfvars            # Production environment overrides
│   ├── dynamodb.tf                # Encrypted DynamoDB Table with AnomalyIndex GSI & TTL
│   ├── sqs.tf                     # SQS Dead-Letter Queue for IoT and Lambda failover
│   ├── logs.tf                    # CloudWatch Log Group with configurable retention
│   ├── sns.tf                     # Encrypted SNS Alert Topic
│   ├── iam.tf                     # Least-privilege IAM roles and policies
│   ├── lambda.tf                  # Lambda resource, dynamic environment variables, X-Ray tracing
│   ├── iot.tf                     # IoT Core Rule, error action fallback, and restricted policy
│   ├── dashboard.tf               # Centralized CloudWatch Operations Dashboard as Code
│   ├── monitoring.tf              # Alarms for errors, throttles, p95 latency, and DLQ messages
│   └── outputs.tf                 # Exports for endpoints, ARNs, and dashboard names
│
├── docs/
│   ├── architecture.md            # Architectural deep dive and component interaction
│   ├── devops_runbook.md          # SRE runbook, DLQ redrive, GSI queries, and incident playbooks
│   └── adr/                       # Architecture Decision Records (ADRs)
│       ├── 0001-record-architecture-decisions.md
│       ├── 0002-dynamodb-gsi-for-anomaly-queries.md
│       ├── 0003-sqs-dead-letter-queue-for-iot-ingestion.md
│       └── 0004-aws-xray-distributed-tracing.md
│
├── Makefile                       # Developer automation (test, lint, format, tf-validate, docker-build)
├── docker-compose.yml             # Compose config for running simulator container locally
└── .pre-commit-config.yaml        # Pre-commit hook validations (black, flake8, tf fmt)
```

---

## 🚨 Anomaly Detection Rules

| Sensor | Normal Range | Anomaly Threshold | Environment Config Variable |
|---|---|---|---|
| Temperature | 15°C – 35°C | < 10°C or > 40°C | `THRESHOLD_TEMP_MIN` / `THRESHOLD_TEMP_MAX` |
| Humidity | 20% – 80% | < 15% or > 90% | `THRESHOLD_HUMI_MIN` / `THRESHOLD_HUMI_MAX` |
| Pressure | 980 – 1050 hPa | < 950 or > 1080 hPa | `THRESHOLD_PRESS_MIN` / `THRESHOLD_PRESS_MAX` |

*Thresholds are managed dynamically via Terraform variables and injected into Lambda environment variables.*

---

## ⚡ Developer & DevOps Automation (Makefile)

Use the root `Makefile` for unified local and CI workflows:

```bash
make help             # View all available make targets
make test             # Run unit tests across all project modules
make test-coverage    # Run unit tests and generate coverage report
make lint             # Check code formatting (Black) and style (Flake8)
make format           # Automatically reformat Python code with Black
make tf-init          # Initialize Terraform providers
make tf-fmt           # Verify Terraform file formatting
make tf-validate      # Validate Terraform syntax and configuration
make tf-plan-dev      # Plan Terraform using dev.tfvars
make docker-build     # Build hardened simulator container image
make docker-run-mock  # Run simulator in offline mock mode (5 iterations)
make clean            # Remove caches and temporary files
```

---

## 🚀 Deployment Guide

### Deploy via Terraform

1. **Deploy Development Environment:**
   ```bash
   cd terraform
   terraform init
   terraform plan -var-file="environments/dev.tfvars"
   terraform apply -var-file="environments/dev.tfvars"
   ```

2. **Deploy Production Environment:**
   ```bash
   terraform plan -var-file="environments/prod.tfvars"
   terraform apply -var-file="environments/prod.tfvars"
   ```

---

## 🧪 Running the Device Simulator

### Option A: Offline Mock Mode (No AWS Certificates Required)
Run the simulator locally or in CI without live AWS credentials:
```bash
MOCK_MODE=true MAX_ITERATIONS=10 python device-simulator/sensor_publisher.py
```

### Option B: Docker Container
```bash
docker-compose up --build -d
```

---

## 📖 Operational Runbook & ADRs
- **Incident Response & SRE Runbook**: See [docs/devops_runbook.md](file:///c:/Users/User/Desktop/IOT%20ANOMALITY/docs/devops_runbook.md) for DLQ redrive procedures, GSI queries, and alert playbooks.
- **Architecture Decision Records**: See [docs/adr/](file:///c:/Users/User/Desktop/IOT%20ANOMALITY/docs/adr/) for context on GSI, DLQ, and X-Ray design choices.

---

## 👤 Author

**Melvin Chacko Jose**
- Email: melvinjose025@gmail.com
- GitHub: [@MelvinjoseC](https://github.com/MelvinjoseC)

---

## 📄 License
MIT License

