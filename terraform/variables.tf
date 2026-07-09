variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, prod)"
  default     = "dev"
}

variable "device_name" {
  type        = string
  description = "Name of the IoT device"
  default     = "RaspberryPi-Sensor-01"
}

variable "alert_email" {
  type        = string
  description = "Email address for SNS anomaly alerts"
  default     = "melvinjos025@gmail.com"
}
