# ─────────────────────────────────────────────────
#  config.py — IoT Anomaly Detection Config
# ─────────────────────────────────────────────────
import os

# AWS IoT Core endpoint
AWS_IOT_ENDPOINT = os.environ.get("AWS_IOT_ENDPOINT", "YOUR_ENDPOINT.iot.us-east-1.amazonaws.com")
AWS_REGION       = os.environ.get("AWS_REGION", "us-east-1")

# MQTT
MQTT_TOPIC  = os.environ.get("MQTT_TOPIC", "sensors/environment")
DEVICE_NAME = os.environ.get("DEVICE_NAME", "RaspberryPi-Sensor-01")

# Certificates
CERT_DIR  = os.environ.get("CERT_DIR", "./certs")
ROOT_CA   = os.environ.get("ROOT_CA", f"{CERT_DIR}/AmazonRootCA1.pem")
CERT_FILE = os.environ.get("CERT_FILE", f"{CERT_DIR}/device-certificate.pem.crt")
KEY_FILE  = os.environ.get("KEY_FILE", f"{CERT_DIR}/private.pem.key")

# Publish interval (seconds)
SEND_INTERVAL = int(os.environ.get("SEND_INTERVAL", "5"))

# Anomaly thresholds
TEMP_MIN  = float(os.environ.get("THRESHOLD_TEMP_MIN", "10.0"))    # °C
TEMP_MAX  = float(os.environ.get("THRESHOLD_TEMP_MAX", "40.0"))    # °C
HUMI_MIN  = float(os.environ.get("THRESHOLD_HUMI_MIN", "15.0"))    # %
HUMI_MAX  = float(os.environ.get("THRESHOLD_HUMI_MAX", "90.0"))    # %
PRESS_MIN = float(os.environ.get("THRESHOLD_PRESS_MIN", "950.0"))   # hPa
PRESS_MAX = float(os.environ.get("THRESHOLD_PRESS_MAX", "1080.0"))  # hPa

# AWS Resources
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "SensorReadings")
SNS_TOPIC_ARN  = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:SensorAnomalyAlerts")
