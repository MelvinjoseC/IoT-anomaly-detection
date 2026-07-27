variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]+$", var.aws_region))
    error_message = "The aws_region variable must be a valid AWS region format (e.g., us-east-1)."
  }
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "The environment variable must be one of: dev, staging, prod."
  }
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

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alert_email))
    error_message = "The alert_email variable must be a valid email address."
  }
}
