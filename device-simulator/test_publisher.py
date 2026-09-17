import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add device-simulator to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sensor_publisher  # noqa: E402
import config  # noqa: E402


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

    @patch("sensor_publisher.mqtt.Client")
    def test_setup_mqtt(self, mock_mqtt):
        sensor_publisher.MOCK_MODE = False
        mock_client = MagicMock()
        mock_mqtt.return_value = mock_client

        client = sensor_publisher.setup_mqtt()
        self.assertEqual(client, mock_client)
        mock_client.tls_set.assert_called_once()

    def test_setup_mqtt_mock_mode(self):
        sensor_publisher.MOCK_MODE = True
        client = sensor_publisher.setup_mqtt()
        self.assertIsInstance(client, sensor_publisher.MockMqttClient)

    def test_mock_mqtt_client_operations(self):
        client = sensor_publisher.MockMqttClient("test-device")
        client.tls_set()
        client.connect("example.com")
        client.loop_start()
        client.publish("test/topic", '{"test": 1}', qos=1)
        client.loop_stop()
        client.disconnect()

    def test_read_sensors_zero_anomaly_rate(self):
        sensor_publisher.ANOMALY_RATE_PERCENT = 0
        for _ in range(15):
            data = sensor_publisher.read_sensors()
            self.assertTrue(20 <= data["temperature"] <= 32)
            self.assertTrue(40 <= data["humidity"] <= 75)
            self.assertTrue(1000 <= data["pressure"] <= 1025)
        # Restore default
        sensor_publisher.ANOMALY_RATE_PERCENT = 10

    def test_read_sensors_100_percent_anomaly_rate(self):
        sensor_publisher.ANOMALY_RATE_PERCENT = 100
        data = sensor_publisher.read_sensors()
        temp = data["temperature"]
        humi = data["humidity"]
        press = data["pressure"]
        is_anomaly = (42 <= temp <= 50) or (5 <= humi <= 12) or (1085 <= press <= 1100)
        self.assertTrue(is_anomaly)
        # Restore default
        sensor_publisher.ANOMALY_RATE_PERCENT = 10

    def test_shutdown_handler(self):
        sensor_publisher.running = True
        sensor_publisher.shutdown_handler(2, None)
        self.assertFalse(sensor_publisher.running)
        sensor_publisher.running = True

    def test_main_mock_mode_execution(self):
        sensor_publisher.MOCK_MODE = True
        sensor_publisher.MAX_ITERATIONS = 1
        sensor_publisher.SEND_INTERVAL = 0
        sensor_publisher.running = True
        sensor_publisher.main()
        self.assertFalse(sensor_publisher.MOCK_MODE is None)


if __name__ == "__main__":
    unittest.main()
