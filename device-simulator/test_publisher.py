import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add device-simulator to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sensor_publisher
import config

class TestSensorPublisher(unittest.TestCase):
    def setUp(self):
        # Reset the tick count on read_sensors
        if hasattr(sensor_publisher.read_sensors, "tick"):
            delattr(sensor_publisher.read_sensors, "tick")

    def test_read_sensors_structure(self):
        data = sensor_publisher.read_sensors()
        self.assertIsNotNone(data)
        self.assertEqual(data["device_id"], config.DEVICE_NAME)
        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("pressure", data)
        self.assertIn("timestamp", data)
        self.assertEqual(data["status"], "ok")

    def test_read_sensors_values_within_range(self):
        # Read multiple times and assert they match simulated values (or anomalies)
        for _ in range(9):
            data = sensor_publisher.read_sensors()
            # Temperature should be normal range (20 to 32)
            self.assertTrue(20 <= data["temperature"] <= 32)
            self.assertTrue(40 <= data["humidity"] <= 75)
            self.assertTrue(1000 <= data["pressure"] <= 1025)

    def test_read_sensors_anomaly_injection(self):
        # The 10th call should trigger an anomaly
        for _ in range(9):
            sensor_publisher.read_sensors()
        
        # 10th tick
        data = sensor_publisher.read_sensors()
        # It should be one of the anomalies
        temp = data["temperature"]
        humi = data["humidity"]
        press = data["pressure"]
        
        # Assert that at least one is in the anomaly range
        is_anomaly = (42 <= temp <= 50) or (5 <= humi <= 12) or (1085 <= press <= 1100)
        self.assertTrue(is_anomaly)

    @patch('sensor_publisher.mqtt.Client')
    def test_setup_mqtt(self, mock_mqtt):
        mock_client = MagicMock()
        mock_mqtt.return_value = mock_client
        
        client = sensor_publisher.setup_mqtt()
        self.assertEqual(client, mock_client)
        mock_client.tls_set.assert_called_once()

if __name__ == "__main__":
    unittest.main()
