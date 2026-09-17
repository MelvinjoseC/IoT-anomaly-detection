resource "aws_dynamodb_table" "sensor_readings" {
  name         = "SensorReadings"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "device_id"
  range_key    = "timestamp"

  attribute {
    name = "device_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "is_anomaly_idx"
    type = "S"
  }

  global_secondary_index {
    name            = "AnomalyIndex"
    hash_key        = "is_anomaly_idx"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = null # Default AWS Managed KMS Key (aws/dynamodb)
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "IoT-Sensor-Readings"
  }
}
