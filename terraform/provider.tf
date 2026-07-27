terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  # Production S3 Backend with DynamoDB state locking configuration (example)
  # backend "s3" {
  #   bucket         = "iot-anomaly-detection-tfstate"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "iot-anomaly-detection-tflocks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge(
      {
        Environment = var.environment
        Project     = "IoT-Anomaly-Detection"
        ManagedBy   = "Terraform"
      },
      var.extra_tags
    )
  }
}
