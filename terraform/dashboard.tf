resource "aws_cloudwatch_dashboard" "iot_system_dashboard" {
  dashboard_name = "IoT-Anomaly-Detection-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.iot_anomaly_detector.function_name, { stat = "Sum", period = 60, color = "#2ca02c" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.iot_anomaly_detector.function_name, { stat = "Sum", period = 60, color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Invocations & Errors"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.iot_anomaly_detector.function_name, { stat = "p50", period = 60, label = "p50" }],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.iot_anomaly_detector.function_name, { stat = "p90", period = 60, label = "p90" }],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.iot_anomaly_detector.function_name, { stat = "p99", period = 60, label = "p99" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Latency Percentiles (Duration ms)"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Throttles", "FunctionName", aws_lambda_function.iot_anomaly_detector.function_name, { stat = "Sum", period = 60, color = "#ff7f0e" }],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.iot_dlq.name, { stat = "Average", period = 60, color = "#9467bd" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Throttles & SQS DLQ Backlog"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.sensor_readings.name, { stat = "Sum", period = 60 }],
            ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", "TableName", aws_dynamodb_table.sensor_readings.name, { stat = "Sum", period = 60 }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "DynamoDB Consumed Capacity Units"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          query  = "SOURCE '${aws_cloudwatch_log_group.lambda_log_group.name}' | fields @timestamp, level, message, device_id, error | filter level in ['WARNING', 'ERROR'] | sort @timestamp desc | limit 25"
          region = var.aws_region
          title  = "Recent Anomaly & Error Events (Logs Insights)"
          view   = "table"
        }
      }
    ]
  })
}
