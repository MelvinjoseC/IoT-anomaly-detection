# 📖 IoT Anomaly Detection System — DevOps Runbook

This guide contains operation guidelines, troubleshooting guides, monitoring dashboard configurations, and incident response procedures for the IoT Anomaly Detection System.

---

## 📐 1. Operational Overview
The system processes IoT data streams via:
1. **Telemetry Ingestion**: MQTT client publishes sensor metrics to AWS IoT Core (Port 8883).
2. **Event Filtering**: IoT Rule matches messages on `sensors/environment` and invokes Lambda.
3. **Detection & Alerts**: Lambda checks thresholds, writes to DynamoDB, and sends SNS alerts on anomalies.

---

## 📊 2. Monitoring & Alerting Infrastructure

### Centralized CloudWatch Dashboard as Code
A centralized CloudWatch Dashboard (`IoT-Anomaly-Detection-<env>`) is provisioned automatically via Terraform (`dashboard.tf`). It provides real-time visualization of:
- **Lambda Metrics**: Invocations vs Errors (Sum, 1m), Latency percentiles (p50, p90, p99), and Invocations Throttles.
- **DynamoDB Metrics**: Consumed Read and Write Capacity Units.
- **SQS DLQ Depth**: `ApproximateNumberOfMessagesVisible` alerting to any backlog of failed messages.
- **Embedded CloudWatch Logs Insights**: Live stream of warning and error events.

### CloudWatch Metric Alarms
| Alarm Name | Metric | Threshold | Action |
|---|---|---|---|
| `AnomalyLambdaErrors` | `Errors` | Sum > 5 in 5m | SNS Alert |
| `AnomalyLambdaThrottles` | `Throttles` | Sum > 0 in 1m | SNS Alert |
| `AnomalyLambdaHighDuration`| `Duration` (p95) | > 10,000 ms in 5m | SNS Alert |
| `AnomalyDLQMessagesVisible`| `ApproximateNumberOfMessagesVisible` | Sum > 0 in 1m | SNS Alert |

### CloudWatch Logs Insights Queries
To investigate issues, use these CloudWatch Logs Insights queries on the `/aws/lambda/IoTAnomalyDetector` log group:

* **Find all anomaly detections:**
  ```sql
  fields @timestamp, device_id, anomalies.0.type, anomalies.0.value
  | filter level = "WARNING" and message like /Anomaly/
  | sort @timestamp desc
  | limit 50
  ```

* **Search for application exceptions:**
  ```sql
  fields @timestamp, message, error
  | filter level = "ERROR"
  | sort @timestamp desc
  | limit 20
  ```

### DynamoDB Global Secondary Index (GSI) Query
Query recent anomalies chronologically across all IoT devices without performing costly table scans:
```bash
aws dynamodb query \
  --table-name SensorReadings \
  --index-name AnomalyIndex \
  --key-condition-expression "is_anomaly_idx = :anomaly_val" \
  --expression-attribute-values '{":anomaly_val": {"S": "TRUE"}}' \
  --scan-index-forward false \
  --limit 25
```

---

## 🚨 3. Incident Response Playbook

### Incident: Dead-Letter Queue (DLQ) Backlog Alert (`AnomalyDLQMessagesVisible`)
* **Symptom**: CloudWatch alarm indicates messages are landing in `iot-anomaly-dead-letter-queue`.
* **Impact**: Unhandled telemetry or Lambda invocations failed to complete normally.
* **Troubleshooting Steps**:
  1. Inspect the DLQ message contents using AWS CLI:
     ```bash
     QUEUE_URL=$(aws sqs get-queue-url --queue-name iot-anomaly-dead-letter-queue --query 'QueueUrl' --output text)
     aws sqs receive-message --queue-url "$QUEUE_URL" --max-number-of-messages 5 --attribute-names All
     ```
  2. Check if messages were redirected from IoT Topic Rule `error_action` or Lambda asynchronous retry failure.
  3. Resolve root cause (e.g. Lambda bug, DynamoDB capacity, AWS service outage).
  4. Redrive DLQ messages back to Lambda or the ingest topic using AWS SQS Dead-Letter Queue Redrive.

### Incident: Lambda Throttling (`AnomalyLambdaThrottles`)
* **Symptom**: `AnomalyLambdaThrottles` alarm fires.
* **Troubleshooting Steps**:
  1. Check account-level Lambda unreserved concurrency limits.
  2. If multiple Lambdas are running concurrently in the region, check concurrency distribution.
  3. Increase account concurrency limit via AWS Support or configure provisioned concurrency if required.

### Incident: Alert Emails/SMS Not Being Received
* **Symptom**: Sensor telemetry indicates anomalies, DynamoDB shows `is_anomaly = true` and `alert_sent = true`, but no alert email/SMS is received.
* **Troubleshooting Steps**:
  1. Check if the email address is confirmed. The SNS Subscription status must be `Confirmed` in the AWS console, not `PendingConfirmation`.
  2. Verify that the SNS Topic encryption (KMS) is properly configured and the Lambda execution role has the required permissions.
  3. Inspect CloudWatch logs for SNS publication errors:
     ```sql
     filter message like /SNS/
     ```

### Incident: Lambda Errors Alarm Firing (`AnomalyLambdaErrors`)
* **Symptom**: CloudWatch Alarm `AnomalyLambdaErrors` is in `ALARM` state.
* **Troubleshooting Steps**:
  1. Check the Log Group `/aws/lambda/IoTAnomalyDetector`.
  2. Identify the root cause (e.g. ValueError due to missing fields, DynamoDB provisioned throughput exceeded, or connection timeouts).
  3. If missing fields: Ensure the publisher is publishing the correct schema.
  4. If DynamoDB errors: Check table status and capacity scaling.

### Incident: Device Simulator Fails to Connect
* **Symptom**: Device simulator logs: `Connection failed. Return code: X` or `TLS connection error`.
* **Troubleshooting Steps**:
  1. Check network configuration (Outbound port 8883 must be open).
  2. Verify the endpoint name `AWS_IOT_ENDPOINT` in `config.py` matches your IoT Core Endpoint address.
  3. Validate certs directory and file names. Ensure `AmazonRootCA1.pem`, `device-certificate.pem.crt`, and `private.pem.key` are present and correct.
  4. Alternatively, use `MOCK_MODE=true` to test simulation locally without TLS certificates.

---

## 💾 4. Disaster Recovery (DR) & Backup Strategy

### DynamoDB State Backup
* **Point-In-Time-Recovery (PITR)** is enabled by default on the `SensorReadings` table. PITR provides continuous backups for up to 35 days, protecting against accidental writes/deletes.
* **Recovery Procedure**:
  1. In the DynamoDB Console, choose the `SensorReadings` table.
  2. Select the **Backups** tab.
  3. Click **Restore to Point-in-Time**.
  4. Specify the date/time and the name of the new target table.
  5. Update the Terraform configurations or Lambda environment variables if the table name changed.
