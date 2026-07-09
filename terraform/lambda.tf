data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/lambda_function.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}

resource "aws_lambda_function" "iot_anomaly_detector" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "IoTAnomalyDetector"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 15

  environment {
    variables = {
      AWS_REGION     = var.aws_region
      DYNAMODB_TABLE = aws_dynamodb_table.sensor_readings.name
      SNS_TOPIC_ARN  = aws_sns_topic.sensor_anomaly_alerts.arn
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_attach
  ]
}
