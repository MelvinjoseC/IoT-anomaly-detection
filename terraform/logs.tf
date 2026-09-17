resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/IoTAnomalyDetector"
  retention_in_days = var.log_retention_days
}
