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
from datetime import datetime, timezone
from decimal import Decimal

# ── Logging ───────────────────────────────────────
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(level, message, **kwargs):
    """Structured JSON logger helper."""
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    logger.log(getattr(logging, level.upper(), logging.INFO), json.dumps(log_data))

# ── AWS Clients ───────────────────────────────────
AWS_REGION     = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "SensorReadings")
SNS_TOPIC_ARN  = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:SensorAnomalyAlerts")

# Lazy load boto3 clients to allow easier unit mocking/testing
dynamodb = None
sns      = None
table    = None

def get_db_table():
    global dynamodb, table
    if table is None:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table    = dynamodb.Table(DYNAMODB_TABLE)
    return table

def get_sns_client():
    global sns
    if sns is None:
        sns = boto3.client("sns", region_name=AWS_REGION)
    return sns

# ── Anomaly Thresholds ────────────────────────────
def get_thresholds():
    """Returns thresholds loaded from environment variables with defaults."""
    return {
        "temperature": {
            "min": float(os.environ.get("THRESHOLD_TEMP_MIN", "10.0")),
            "max": float(os.environ.get("THRESHOLD_TEMP_MAX", "40.0")),
            "unit": "°C"
        },
        "humidity": {
            "min": float(os.environ.get("THRESHOLD_HUMI_MIN", "15.0")),
            "max": float(os.environ.get("THRESHOLD_HUMI_MAX", "90.0")),
            "unit": "%"
        },
        "pressure": {
            "min": float(os.environ.get("THRESHOLD_PRESS_MIN", "950.0")),
            "max": float(os.environ.get("THRESHOLD_PRESS_MAX", "1080.0")),
            "unit": "hPa"
        },
    }

# ── Anomaly Detection ─────────────────────────────
def detect_anomalies(data):
    """
    Check each sensor value against thresholds.
    Returns list of anomaly dicts (empty if all normal).
    """
    anomalies = []
    thresholds = get_thresholds()

    for sensor, limits in thresholds.items():
        value = data.get(sensor)
        if value is None:
            continue

        try:
            value = float(value)
        except (ValueError, TypeError):
            continue

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

    client = get_sns_client()
    response = client.publish(
        TopicArn = SNS_TOPIC_ARN,
        Message  = message,
        Subject  = subject[:100]  # SNS subject max 100 chars
    )
    log_event("INFO", f"SNS alert sent", message_id=response['MessageId'])
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
        "is_anomaly"    : len(anomalies) > 0,
        "is_anomaly_idx": "TRUE" if len(anomalies) > 0 else "FALSE",
        "anomaly_types" : [a["type"] for a in anomalies],
        "alert_sent"    : alert_sent,
        "stored_at"     : datetime.now(timezone.utc).isoformat()
    }
    
    # Calculate TTL (30 days from now)
    try:
        epoch_now = int(datetime.now(timezone.utc).timestamp())
        item["ttl"] = epoch_now + (30 * 24 * 60 * 60)
    except Exception as e:
        log_event("ERROR", "Failed to calculate TTL", error=str(e))

    db_table = get_db_table()
    db_table.put_item(Item=item)

# ── Main Handler ──────────────────────────────────
def lambda_handler(event, context):
    """
    Triggered by AWS IoT Rule.
    1. Detect anomalies in sensor data
    2. Send SNS alert if anomaly found
    3. Store reading in DynamoDB
    """
    log_event("INFO", "Received incoming IoT Core event", event=event)

    try:
        # ── Validate ──────────────────────────────
        required = ["device_id", "timestamp", "temperature", "humidity"]
        for f in required:
            if f not in event or event[f] is None:
                raise ValueError(f"Missing required field: {f}")

        # ── Detect anomalies ──────────────────────
        anomalies  = detect_anomalies(event)
        alert_sent = False

        if anomalies:
            log_event(
                "WARNING", 
                "Anomaly detected in sensor reading", 
                device_id=event['device_id'], 
                anomalies=anomalies
            )
            send_alert(event, anomalies)
            alert_sent = True
        else:
            log_event("INFO", "Normal reading processed", device_id=event['device_id'])

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
        log_event("ERROR", "Validation failure", error=str(ve))
        return {"statusCode": 400, "error": str(ve)}

    except Exception as e:
        log_event("ERROR", "Unexpected exception occurred", error=str(e))
        return {"statusCode": 500, "error": "Internal error"}
