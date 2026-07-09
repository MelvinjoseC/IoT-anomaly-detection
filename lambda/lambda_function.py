"""
lambda_function.py
────────────────────────────────────────────────────────
AWS Lambda triggered by AWS IoT Core Rule.
Checks sensor readings for anomalies and fires SNS alerts.

Trigger : AWS IoT Rule (Topic: sensors/environment)
Output  : DynamoDB (all readings) + SNS (anomalies only)
Author  : Melvin Chacko Jose
────────────────────────────────────────────────────────
"""

import json
import os
import boto3
import logging
from datetime import datetime
from decimal import Decimal

# ── Logging ───────────────────────────────────────
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── AWS Clients ───────────────────────────────────
AWS_REGION     = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "SensorReadings")
SNS_TOPIC_ARN  = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:SensorAnomalyAlerts")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
sns      = boto3.client("sns",      region_name=AWS_REGION)
table    = dynamodb.Table(DYNAMODB_TABLE)


# ── Anomaly Thresholds ────────────────────────────
THRESHOLDS = {
    "temperature": {"min": 10.0,  "max": 40.0,  "unit": "°C"},
    "humidity"   : {"min": 15.0,  "max": 90.0,  "unit": "%"},
    "pressure"   : {"min": 950.0, "max": 1080.0, "unit": "hPa"},
}

# ── Anomaly Detection ─────────────────────────────
def detect_anomalies(data):
    """
    Check each sensor value against thresholds.
    Returns list of anomaly dicts (empty if all normal).
    """
    anomalies = []

    for sensor, limits in THRESHOLDS.items():
        value = data.get(sensor)
        if value is None:
            continue

        value = float(value)

        if value < limits["min"]:
            anomalies.append({
                "sensor"    : sensor,
                "value"     : value,
                "unit"      : limits["unit"],
                "type"      : f"LOW_{sensor.upper()}",
                "threshold" : limits["min"],
                "direction" : "below minimum"
            })
        elif value > limits["max"]:
            anomalies.append({
                "sensor"    : sensor,
                "value"     : value,
                "unit"      : limits["unit"],
                "type"      : f"HIGH_{sensor.upper()}",
                "threshold" : limits["max"],
                "direction" : "above maximum"
            })

    return anomalies

# ── Build SNS Alert Message ───────────────────────
def build_alert_message(data, anomalies):
    """Build a clear, readable alert message."""
    lines = [
        "🚨 ANOMALY ALERT — IoT Sensor System",
        "=" * 45,
        f"Device    : {data.get('device_id', 'Unknown')}",
        f"Timestamp : {data.get('timestamp', 'Unknown')}",
        "",
        "⚠️  Anomalies Detected:",
    ]

    for a in anomalies:
        lines.append(
            f"  • {a['type']}: {a['value']}{a['unit']} "
            f"({a['direction']} threshold of {a['threshold']}{a['unit']})"
        )

    lines += [
        "",
        "📊 Full Reading:",
        f"  Temperature : {data.get('temperature', 'N/A')}°C",
        f"  Humidity    : {data.get('humidity', 'N/A')}%",
        f"  Pressure    : {data.get('pressure', 'N/A')} hPa",
        "",
        "⚡ Action: Immediate inspection required!",
        "=" * 45,
    ]

    return "\n".join(lines)

# ── Send SNS Alert ────────────────────────────────
def send_alert(data, anomalies):
    """Publish anomaly alert to SNS topic."""
    message = build_alert_message(data, anomalies)
    subject = f"🚨 IoT Alert: {', '.join(a['type'] for a in anomalies)}"

    response = sns.publish(
        TopicArn = SNS_TOPIC_ARN,
        Message  = message,
        Subject  = subject[:100]  # SNS subject max 100 chars
    )
    logger.info(f"SNS alert sent: MessageId={response['MessageId']}")
    return response["MessageId"]

# ── Store to DynamoDB ─────────────────────────────
def store_reading(data, anomalies, alert_sent):
    """Store sensor reading with anomaly metadata."""
    item = {
        "device_id"  : data["device_id"],
        "timestamp"  : data["timestamp"],
        "temperature": Decimal(str(data.get("temperature", 0))),
        "humidity"   : Decimal(str(data.get("humidity", 0))),
        "pressure"   : Decimal(str(data.get("pressure", 0))),
        "is_anomaly" : len(anomalies) > 0,
        "anomaly_types": [a["type"] for a in anomalies],
        "alert_sent" : alert_sent,
        "stored_at"  : datetime.utcnow().isoformat() + "Z"
    }
    table.put_item(Item=item)

# ── Main Handler ──────────────────────────────────
def lambda_handler(event, context):
    """
    Triggered by AWS IoT Rule.
    1. Detect anomalies in sensor data
    2. Send SNS alert if anomaly found
    3. Store reading in DynamoDB
    """
    logger.info(f"Received: {json.dumps(event)}")

    try:
        # ── Validate ──────────────────────────────
        required = ["device_id", "timestamp", "temperature", "humidity"]
        for f in required:
            if f not in event:
                raise ValueError(f"Missing field: {f}")

        # ── Detect anomalies ──────────────────────
        anomalies  = detect_anomalies(event)
        alert_sent = False

        if anomalies:
            logger.warning(
                f"🚨 ANOMALY on {event['device_id']}: "
                f"{[a['type'] for a in anomalies]}"
            )
            send_alert(event, anomalies)
            alert_sent = True
        else:
            logger.info(f"✅ Normal reading from {event['device_id']}")

        # ── Store to DynamoDB ─────────────────────
        store_reading(event, anomalies, alert_sent)

        return {
            "statusCode"  : 200,
            "device_id"   : event["device_id"],
            "is_anomaly"  : len(anomalies) > 0,
            "anomaly_count": len(anomalies),
            "alert_sent"  : alert_sent
        }

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return {"statusCode": 400, "error": str(ve)}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"statusCode": 500, "error": "Internal error"}
