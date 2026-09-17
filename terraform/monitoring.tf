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

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "AnomalyLambdaThrottles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alerts immediately when Lambda concurrency throttling occurs"
  alarm_actions       = [aws_sns_topic.sensor_anomaly_alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.iot_anomaly_detector.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_high_duration" {
  alarm_name          = "AnomalyLambdaHighDuration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = 10000 # 10 seconds (near 15s timeout)
  alarm_description   = "Alerts when Lambda p95 duration exceeds 10 seconds"
  alarm_actions       = [aws_sns_topic.sensor_anomaly_alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.iot_anomaly_detector.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "sqs_dlq_messages" {
  alarm_name          = "AnomalyDLQMessagesVisible"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alerts when messages land in the IoT / Lambda Dead-Letter Queue"
  alarm_actions       = [aws_sns_topic.sensor_anomaly_alerts.arn]

  dimensions = {
    QueueName = aws_sqs_queue.iot_dlq.name
  }
}

