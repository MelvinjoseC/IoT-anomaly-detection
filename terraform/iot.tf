resource "aws_iot_topic_rule" "sensor_anomaly_rule" {
  name        = "SensorAnomalyRule"
  description = "Routes IoT sensor telemetry to Lambda for anomaly check"
  enabled     = true
  sql         = "SELECT * FROM 'sensors/environment'"
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.iot_anomaly_detector.arn
  }
}

resource "aws_lambda_permission" "allow_iot_core" {
  statement_id  = "AllowExecutionFromIoTCore"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.iot_anomaly_detector.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.sensor_anomaly_rule.arn
}

resource "aws_iot_policy" "anomaly_device_policy" {
  name = "AnomalyDevicePolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["iot:Connect", "iot:Publish", "iot:Subscribe", "iot:Receive"]
        Resource = ["*"]
      }
    ]
  })
}
