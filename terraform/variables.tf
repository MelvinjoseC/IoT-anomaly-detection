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

variable "extra_tags" {
  type        = map(string)
  description = "Extra tags to add to all resources"
  default     = {}
}

variable "threshold_temp_min" {
  type        = number
  description = "Minimum temperature threshold in Celsius"
  default     = 10.0
}

variable "threshold_temp_max" {
  type        = number
  description = "Maximum temperature threshold in Celsius"
  default     = 40.0
}

variable "threshold_humi_min" {
  type        = number
  description = "Minimum humidity threshold in percentage"
  default     = 15.0
}

variable "threshold_humi_max" {
  type        = number
  description = "Maximum humidity threshold in percentage"
  default     = 90.0
}

variable "threshold_press_min" {
  type        = number
  description = "Minimum atmospheric pressure threshold in hPa"
  default     = 950.0
}

variable "threshold_press_max" {
  type        = number
  description = "Maximum atmospheric pressure threshold in hPa"
  default     = 1080.0
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 30

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "The log_retention_days variable must be a valid CloudWatch retention period (e.g. 7, 14, 30, 90)."
  }
}

