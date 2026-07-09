resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "AnomalyLambdaErrors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300 # 5 minutes
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "This alarm monitors Lambda errors for IoTAnomalyDetector and alerts via SNS"
  alarm_actions       = [aws_sns_topic.sensor_anomaly_alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.iot_anomaly_detector.function_name
  }
}
