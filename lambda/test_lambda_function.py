import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the lambda directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import lambda_function  # noqa: E402


class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        # Reset lazy-loaded clients
        lambda_function.dynamodb = None
        lambda_function.sns = None
        lambda_function.table = None

    def test_detect_anomalies_normal(self):
        data = {"temperature": 25.0, "humidity": 50.0, "pressure": 1013.0}
        anomalies = lambda_function.detect_anomalies(data)
        self.assertEqual(len(anomalies), 0)

    def test_detect_anomalies_high_temp(self):
        data = {"temperature": 45.0, "humidity": 50.0, "pressure": 1013.0}
        anomalies = lambda_function.detect_anomalies(data)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["sensor"], "temperature")
        self.assertEqual(anomalies[0]["type"], "HIGH_TEMPERATURE")

    def test_detect_anomalies_low_humidity(self):
        data = {"temperature": 25.0, "humidity": 10.0, "pressure": 1013.0}
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
            "pressure": 1013.0,
        }
        anomalies = lambda_function.detect_anomalies(data)
        msg = lambda_function.build_alert_message(data, anomalies)
        self.assertIn("🚨 ANOMALY ALERT", msg)
        self.assertIn("Test-Device", msg)
        self.assertIn("HIGH_TEMPERATURE", msg)

    @patch("lambda_function.get_db_table")
    @patch("lambda_function.get_sns_client")
    def test_lambda_handler_normal(self, mock_sns, mock_db):
        mock_table_instance = MagicMock()
        mock_db.return_value = mock_table_instance

        event = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "temperature": 25.0,
            "humidity": 50.0,
            "pressure": 1013.0,
        }

        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 200)
        self.assertFalse(res["is_anomaly"])
        self.assertFalse(res["alert_sent"])
        mock_table_instance.put_item.assert_called_once()
        mock_sns.return_value.publish.assert_not_called()

    @patch("lambda_function.get_db_table")
    @patch("lambda_function.get_sns_client")
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
            "pressure": 1013.0,
        }

        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 200)
        self.assertTrue(res["is_anomaly"])
        self.assertTrue(res["alert_sent"])
        mock_table_instance.put_item.assert_called_once()
        mock_sns_client.publish.assert_called_once()

    @patch("lambda_function.get_db_table")
    @patch("lambda_function.get_sns_client")
    def test_lambda_handler_missing_fields(self, mock_sns, mock_db):
        # Missing temperature
        event = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "humidity": 50.0,
        }

        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 400)
        self.assertIn("error", res)

    def test_detect_anomalies_pressure(self):
        # Low pressure
        low_p = lambda_function.detect_anomalies(
            {"temperature": 25.0, "humidity": 50.0, "pressure": 900.0}
        )
        self.assertEqual(len(low_p), 1)
        self.assertEqual(low_p[0]["type"], "LOW_PRESSURE")

        # High pressure
        high_p = lambda_function.detect_anomalies(
            {"temperature": 25.0, "humidity": 50.0, "pressure": 1100.0}
        )
        self.assertEqual(len(high_p), 1)
        self.assertEqual(high_p[0]["type"], "HIGH_PRESSURE")

    def test_detect_anomalies_boundary_values(self):
        # Exact boundary values should not trigger anomaly
        boundary_data = {
            "temperature": 10.0,  # min limit
            "humidity": 90.0,  # max limit
            "pressure": 950.0,  # min limit
        }
        self.assertEqual(len(lambda_function.detect_anomalies(boundary_data)), 0)

        # Values just beyond limits should trigger
        beyond_data = {"temperature": 9.99, "humidity": 90.01, "pressure": 949.99}
        self.assertEqual(len(lambda_function.detect_anomalies(beyond_data)), 3)

    def test_detect_anomalies_invalid_types(self):
        # Non-numeric or None values should be safely skipped without crashing
        bad_data = {"temperature": "not_a_number", "humidity": None, "pressure": 1013.0}
        anomalies = lambda_function.detect_anomalies(bad_data)
        self.assertEqual(len(anomalies), 0)

    def test_custom_environment_thresholds(self):
        with patch.dict(os.environ, {"THRESHOLD_TEMP_MAX": "30.0"}):
            data = {"temperature": 32.0, "humidity": 50.0, "pressure": 1013.0}
            anomalies = lambda_function.detect_anomalies(data)
            self.assertEqual(len(anomalies), 1)
            self.assertEqual(anomalies[0]["type"], "HIGH_TEMPERATURE")

    @patch("lambda_function.get_db_table")
    def test_store_reading_gsi_attribute(self, mock_db):
        mock_table = MagicMock()
        mock_db.return_value = mock_table

        # Case 1: Normal reading -> is_anomaly_idx == "FALSE"
        normal_data = {
            "device_id": "Dev-01",
            "timestamp": "2026-07-27T00:00:00Z",
            "temperature": 25.0,
            "humidity": 50.0,
            "pressure": 1013.0,
        }
        lambda_function.store_reading(normal_data, [], False)
        called_item = mock_table.put_item.call_args[1]["Item"]
        self.assertEqual(called_item["is_anomaly_idx"], "FALSE")
        self.assertFalse(called_item["is_anomaly"])

        # Case 2: Anomaly reading -> is_anomaly_idx == "TRUE"
        mock_table.reset_mock()
        anomalies = [{"type": "HIGH_TEMPERATURE"}]
        lambda_function.store_reading(normal_data, anomalies, True)
        called_item_anomaly = mock_table.put_item.call_args[1]["Item"]
        self.assertEqual(called_item_anomaly["is_anomaly_idx"], "TRUE")
        self.assertTrue(called_item_anomaly["is_anomaly"])

    @patch("lambda_function.get_db_table")
    @patch("lambda_function.get_sns_client")
    def test_lambda_handler_internal_error(self, mock_sns, mock_db):
        mock_table = MagicMock()
        mock_table.put_item.side_effect = RuntimeError("DynamoDB connection timeout")
        mock_db.return_value = mock_table

        event = {
            "device_id": "Test-Device",
            "timestamp": "2026-07-27T00:00:00Z",
            "temperature": 25.0,
            "humidity": 50.0,
            "pressure": 1013.0,
        }
        res = lambda_function.lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 500)
        self.assertIn("error", res)


if __name__ == "__main__":
    unittest.main()
