# Development Environment Configurations
aws_region  = "us-east-1"
environment = "dev"
device_name = "RaspberryPi-Sensor-Dev"
alert_email = "melvinjose025@gmail.com"

# Dev environment keeps 7 days of logs to optimize cost
log_retention_days = 7

threshold_temp_min  = 10.0
threshold_temp_max  = 40.0
threshold_humi_min  = 15.0
threshold_humi_max  = 90.0
threshold_press_min = 950.0
threshold_press_max = 1080.0

extra_tags = {
  Environment = "dev"
  Ephemeral   = "false"
}
