data "aws_iot_endpoint" "iot_endpoint" {
  endpoint_type = "iot:Data-ATS"
}

output "iot_endpoint" {
  value       = data.aws_iot_endpoint.iot_endpoint.endpoint_address
  description = "The AWS IoT Core device data endpoint to configure in the simulator"
}

output "sns_topic_arn" {
  value       = aws_sns_topic.sensor_anomaly_alerts.arn
  description = "The ARN of the SNS topic for anomaly notifications"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.sensor_readings.name
  description = "The name of the DynamoDB table storing telemetry readings"
}

output "lambda_arn" {
  value       = aws_lambda_function.iot_anomaly_detector.arn
  description = "The ARN of the Lambda function"
}

output "sqs_dlq_arn" {
  value       = aws_sqs_queue.iot_dlq.arn
  description = "The ARN of the Dead-Letter SQS Queue for failed IoT processing"
}

output "sqs_dlq_url" {
  value       = aws_sqs_queue.iot_dlq.url
  description = "The URL of the Dead-Letter SQS Queue for failed IoT processing"
}

output "cloudwatch_dashboard_name" {
  value       = aws_cloudwatch_dashboard.iot_system_dashboard.dashboard_name
  description = "Name of the centralized CloudWatch operations dashboard"
}

