resource "aws_iam_role" "lambda_execution" {
  name = "anomaly-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "anomaly-lambda-policy"
  description = "Least-privilege IAM policy for IoT Anomaly Detector Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # CloudWatch Logs (Restricted to specific log group)
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_cloudwatch_log_group.lambda_log_group.arn,
          "${aws_cloudwatch_log_group.lambda_log_group.arn}:*"
        ]
      },
      # DynamoDB Access (least-privilege)
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.sensor_readings.arn,
          "${aws_dynamodb_table.sensor_readings.arn}/index/*"
        ]
      },
      # SNS Publish Access (least-privilege)
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.sensor_anomaly_alerts.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
