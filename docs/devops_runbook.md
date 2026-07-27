# 📖 IoT Anomaly Detection System — DevOps Runbook

This guide contains operation guidelines, troubleshooting guides, monitoring dashboard configurations, and incident response procedures for the IoT Anomaly Detection System.

---

## 📐 1. Operational Overview
The system processes IoT data streams via:
1. **Telemetry Ingestion**: MQTT client publishes sensor metrics to AWS IoT Core (Port 8883).
2. **Event Filtering**: IoT Rule matches messages on `sensors/environment` and invokes Lambda.
3. **Detection & Alerts**: Lambda checks thresholds, writes to DynamoDB, and sends SNS alerts on anomalies.

---

## 📊 2. Monitoring & Alerting Recommendations

### Recommended CloudWatch Dashboard Layout
We recommend setting up a central CloudWatch Dashboard containing the following metrics:
- **Lambda Function**:
  - `Invocations` (Sum, 1m period)
  - `Errors` (Sum, 1m period) — Trigger alarm if > 0.
  - `Duration` (p95, p99, 1m period)
- **DynamoDB**:
  - `WriteThrottleEvents` (Sum, 5m period)
  - `ConsumedWriteCapacityUnits` (Average, 5m period)
- **AWS IoT Core**:
  - `Connect.Success` / `Connect.AuthError` (Sum)
  - `PublishIn.Success` / `PublishIn.Failure` (Sum)

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

---

## 🚨 3. Incident Response Playbook

### Incident: Alert Emails/SMS Not Being Received
* **Symptom**: Sensor telemetry indicates anomalies, DynamoDB shows `is_anomaly = true` and `alert_sent = true`, but no alert email/SMS is received.
* **Troubleshooting Steps**:
  1. Check if the email address is confirmed. The SNS Subscription status must be `Confirmed` in the AWS console, not `PendingConfirmation`.
  2. Verify that the SNS Topic encryption (KMS) is properly configured and the Lambda execution role has the required `kms:GenerateDataKey` and `kms:Decrypt` privileges (if using a custom key; if using the default `alias/aws/sns` AWS key, ensure IAM is using standard paths).
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
  4. Check if the IoT policy in AWS IoT Core has been attached to the certificate.

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
