# ☁️ AWS Setup Guide — IoT Anomaly Detection System

> [!TIP]
> **Prefer Automation?** You can automate this entire guide using the Terraform configuration files in the `terraform/` directory. See the `README.md` for quick start instructions.

If you prefer to set up everything manually via the AWS Console, follow these steps in order. Takes about 30–40 minutes.


---

## Step 1 — Create DynamoDB Table

1. **AWS Console → DynamoDB → Create Table**
2. Table name: `SensorReadings`
3. Partition key: `device_id` (String)
4. Sort key: `timestamp` (String)
5. Click **Create**

---

## Step 2 — Create SNS Topic & Subscriptions

### 2a — Create Topic
1. **AWS Console → SNS → Topics → Create Topic**
2. Type: **Standard**
3. Name: `SensorAnomalyAlerts`
4. Click **Create Topic**
5. Copy the **ARN** (looks like `arn:aws:sns:us-east-1:123456789:SensorAnomalyAlerts`)
6. Paste this ARN into `lambda/lambda_function.py` → `SNS_TOPIC_ARN`

### 2b — Subscribe Email
1. In your topic → **Create Subscription**
2. Protocol: **Email**
3. Endpoint: your email address
4. Click **Create Subscription**
5. **Check your email → click Confirm Subscription link**

### 2c — Subscribe SMS (Optional)
1. Create another subscription
2. Protocol: **SMS**
3. Endpoint: `+91XXXXXXXXXX` (your phone with country code)
4. Click **Create Subscription**

---

## Step 3 — Create IAM Role for Lambda

1. **IAM → Roles → Create Role**
2. Trusted entity: **Lambda**
3. Add permissions:
   - `AmazonDynamoDBFullAccess`
   - `AmazonSNSFullAccess`
   - `AWSLambdaBasicExecutionRole`
   - `AWSIoTFullAccess`
4. Role name: `anomaly-lambda-role`
5. Click **Create**

---

## Step 4 — Create Lambda Function

1. **Lambda → Create Function**
2. Name: `IoTAnomalyDetector`
3. Runtime: **Python 3.11**
4. Execution role: `anomaly-lambda-role`
5. Click **Create Function**
6. Paste code from `lambda/lambda_function.py`
7. Update `SNS_TOPIC_ARN` with your actual ARN from Step 2
8. Click **Deploy**

---

## Step 5 — Set Up AWS IoT Core

### 5a — Create IoT Thing
1. **IoT Core → Manage → Things → Create Thing**
2. Name: `RaspberryPi-Sensor-01`
3. Auto-generate certificate
4. **Download all 4 certificates** → put in `device-simulator/certs/`

### 5b — Create IoT Policy
1. **IoT Core → Security → Policies → Create**
2. Name: `AnomalyDevicePolicy`
3. JSON:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["iot:Connect", "iot:Publish", "iot:Subscribe", "iot:Receive"],
      "Resource": "*"
    }
  ]
}
```

### 5c — Create IoT Rule (IoT Core → Lambda)
1. **IoT Core → Message Routing → Rules → Create**
2. Name: `SensorAnomalyRule`
3. SQL:
```sql
SELECT * FROM 'sensors/environment'
```
4. Action: **Lambda function → IoTAnomalyDetector**
5. Click **Create Rule**

### 5d — Get IoT Endpoint
1. **IoT Core → Settings**
2. Copy **Device data endpoint**
3. Paste into `device-simulator/config.py` → `AWS_IOT_ENDPOINT`

---

## Step 6 — Set Up CloudWatch Alarm

1. **CloudWatch → Alarms → Create Alarm**
2. Metric: **Lambda → By Function Name → IoTAnomalyDetector → Errors**
3. Condition: Errors > 5 in 5 minutes
4. Action: Send SNS notification to `SensorAnomalyAlerts`
5. Alarm name: `AnomalyLambdaErrors`

---

## Step 7 — Run the Simulator

```bash
cd device-simulator
pip install -r requirements.txt
python sensor_publisher.py
```

Wait for the 10th reading — an anomaly will be injected automatically and you'll receive an email/SMS alert! 🚨

---

## ✅ Verify Everything

```
sensor_publisher.py runs
→ IoT Core receives data
→ Lambda triggered
→ Anomaly detected every ~10 readings
→ SNS fires email + SMS alert 📧📱
→ DynamoDB stores all readings with is_anomaly flag
→ CloudWatch shows Lambda invocations
```

---

## 💰 Cost Estimate (Free Tier)

| Service | Free Tier |
|---|---|
| IoT Core | 250K messages/month free |
| Lambda | 1M requests/month free |
| DynamoDB | 25 GB free |
| SNS | 1M notifications/month free |
| CloudWatch | 10 metrics free |

**Total: $0** within free tier ✅
