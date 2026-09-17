resource "aws_sqs_queue" "iot_dlq" {
  name                      = "iot-anomaly-dead-letter-queue"
  message_retention_seconds = 1209600 # 14 days
  sqs_managed_sse_enabled   = true

  tags = {
    Name        = "IoT-Anomaly-DLQ"
    Description = "Dead-letter queue for failed IoT topic messages and Lambda errors"
  }
}
