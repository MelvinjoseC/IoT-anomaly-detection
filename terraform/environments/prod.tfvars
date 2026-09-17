# Production Environment Configurations
aws_region  = "us-east-1"
environment = "prod"
device_name = "RaspberryPi-Sensor-Prod-01"
alert_email = "melvinjose025@gmail.com"

# Production environment retains 90 days of logs for audit compliance
log_retention_days = 90

# Stricter production anomaly limits
threshold_temp_min  = 12.0
threshold_temp_max  = 38.0
threshold_humi_min  = 20.0
threshold_humi_max  = 85.0
threshold_press_min = 960.0
threshold_press_max = 1060.0

extra_tags = {
  Environment    = "prod"
  Criticality    = "tier-1"
  DataClassifier = "confidential"
}
