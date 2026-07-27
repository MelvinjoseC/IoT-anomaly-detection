resource "aws_sns_topic" "sensor_anomaly_alerts" {
  name              = "SensorAnomalyAlerts"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.sensor_anomaly_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
