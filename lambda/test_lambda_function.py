import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the lambda directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import lambda_function

class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        # Reset lazy-loaded clients
        lambda_function.dynamodb = None
        lambda_function.sns = None
        lambda_function.table = None

    def test_detect_anomalies_normal(self):
        data = {
            "temperature": 25.0,
            "humidity": 50.0,
            "pressure": 1013.0
        }
        anomalies = lambda_function.detect_anomalies(data)
        self.assertEqual(len(anomalies), 0)

    def test_detect_anomalies_high_temp(self):
        data = {
            "temperature": 45.0,
            "humidity": 50.0,
            "pressure": 1013.0
        }
        anomalies = lambda_function.detect_anomalies(data)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["sensor"], "temperature")
        self.assertEqual(anomalies[0]["type"], "HIGH_TEMPERATURE")

    def test_detect_anomalies_low_humidity(self):
        data = {
            "temperature": 25.0,
            "humidity": 10.0,
            "pressure": 1013.0
        }
        anomalies = lambda_function.detect_anomalies(data)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["sensor"], "humidity")
        self.assertEqual(anomalies[0]["type"], "LOW_HUMIDITY")

    def test_build_alert_message(self):
        data = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "temperature": 45.0,
            "humidity": 50.0,
            "pressure": 1013.0
        }
        anomalies = lambda_function.detect_anomalies(data)
        msg = lambda_function.build_alert_message(data, anomalies)
        self.assertIn("🚨 ANOMALY ALERT", msg)
        self.assertIn("Test-Device", msg)
        self.assertIn("HIGH_TEMPERATURE", msg)

    @patch('lambda_function.get_db_table')
    @patch('lambda_function.get_sns_client')
    def test_lambda_handler_normal(self, mock_sns, mock_db):
        mock_table_instance = MagicMock()
        mock_db.return_value = mock_table_instance
        
        event = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "temperature": 25.0,
            "humidity": 50.0,
            "pressure": 1013.0
        }
        
        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 200)
        self.assertFalse(res["is_anomaly"])
        self.assertFalse(res["alert_sent"])
        mock_table_instance.put_item.assert_called_once()
        mock_sns.return_value.publish.assert_not_called()

    @patch('lambda_function.get_db_table')
    @patch('lambda_function.get_sns_client')
    def test_lambda_handler_anomaly(self, mock_sns, mock_db):
        mock_table_instance = MagicMock()
        mock_db.return_value = mock_table_instance
        
        mock_sns_client = MagicMock()
        mock_sns_client.publish.return_value = {"MessageId": "msg-12345"}
        mock_sns.return_value = mock_sns_client

        event = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "temperature": 45.0,
            "humidity": 50.0,
            "pressure": 1013.0
        }
        
        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 200)
        self.assertTrue(res["is_anomaly"])
        self.assertTrue(res["alert_sent"])
        mock_table_instance.put_item.assert_called_once()
        mock_sns_client.publish.assert_called_once()

    @patch('lambda_function.get_db_table')
    @patch('lambda_function.get_sns_client')
    def test_lambda_handler_missing_fields(self, mock_sns, mock_db):
        # Missing temperature
        event = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "humidity": 50.0
        }
        
        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 400)
        self.assertIn("error", res)

if __name__ == "__main__":
    unittest.main()
