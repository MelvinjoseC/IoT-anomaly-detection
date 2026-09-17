"""
sensor_publisher.py
────────────────────────────────────────────────────────
Reads (or simulates) temperature, humidity, and pressure
sensor data and publishes to AWS IoT Core via MQTT.

Occasionally injects anomalies to test the alert system.

Run on: Raspberry Pi + DHT22 sensor, OR any PC (simulation)
Author: Melvin Chacko Jose
────────────────────────────────────────────────────────
"""

import json
import time
import ssl
import random
import datetime
import logging
import signal
import paho.mqtt.client as mqtt
from config import (
    AWS_IOT_ENDPOINT, MQTT_TOPIC, DEVICE_NAME,
    ROOT_CA, CERT_FILE, KEY_FILE, SEND_INTERVAL
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("SensorPublisher")

# Set to True if running on real Raspberry Pi with DHT sensor
USE_REAL_SENSOR = False

if USE_REAL_SENSOR:
    try:
        import Adafruit_DHT
        SENSOR     = Adafruit_DHT.DHT22
        SENSOR_PIN = 17
    except ImportError:
        logger.error("Adafruit_DHT library not found. Falling back to simulation.")
        USE_REAL_SENSOR = False

# Global running state
running = True

# ── Sensor reading ────────────────────────────────
def read_sensors():
    """
    Read from real hardware OR simulate data.
    Every ~10th reading injects an anomaly to test alerts.
    """
    tick = getattr(read_sensors, "tick", 0) + 1
    read_sensors.tick = tick

    if USE_REAL_SENSOR:
        try:
            humidity, temperature = Adafruit_DHT.read_retry(SENSOR, SENSOR_PIN)
            pressure = round(random.uniform(1000, 1020), 2)  # simulated
            if humidity is None or temperature is None:
                return None
        except Exception as e:
            logger.error(f"Hardware sensor read failed: {e}")
            return None
    else:
        # ── Simulate normal readings ──────────────
        temperature = round(random.uniform(20, 32), 2)
        humidity    = round(random.uniform(40, 75), 2)
        pressure    = round(random.uniform(1000, 1025), 2)

    # ── Inject anomaly every ~10 readings ─────────
    if tick % 10 == 0:
        anomaly_type = random.choice(["high_temp", "low_humi", "high_press"])
        if anomaly_type == "high_temp":
            temperature = round(random.uniform(42, 50), 2)
            logger.warning("[ANOMALY INJECTED] High temperature!")
        elif anomaly_type == "low_humi":
            humidity = round(random.uniform(5, 12), 2)
            logger.warning("[ANOMALY INJECTED] Low humidity!")
        else:
            pressure = round(random.uniform(1085, 1100), 2)
            logger.warning("[ANOMALY INJECTED] High pressure!")

    return {
        "device_id"  : DEVICE_NAME,
        "timestamp"  : datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "temperature": temperature,
        "humidity"   : humidity,
        "pressure"   : pressure,
        "unit_temp"  : "Celsius",
        "unit_press" : "hPa",
        "status"     : "ok"
    }

# ── MQTT Callbacks ────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected successfully to AWS IoT Core!")
    else:
        logger.error(f"Connection failed. Return code: {rc}")

def on_disconnect(client, userdata, rc):
    logger.warning(f"Disconnected from AWS IoT Core (rc={rc})")

# ── Setup MQTT ────────────────────────────────────
def setup_mqtt():
    client = mqtt.Client(client_id=DEVICE_NAME)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        client.tls_set(
            ca_certs    = ROOT_CA,
            certfile    = CERT_FILE,
            keyfile     = KEY_FILE,
            tls_version = ssl.PROTOCOL_TLSv1_2
        )
    except FileNotFoundError as e:
        logger.error(f"Certificate files not found: {e}. Secure connection might fail.")
    return client

# ── Graceful Shutdown Handler ────────────────────
def shutdown_handler(signum, frame):
    global running
    logger.info(f"Signal {signum} received. Stopping sensor publisher...")
    running = False

# ── Main ──────────────────────────────────────────
def main():
    logger.info("IoT Anomaly Detection Publisher Starting...")
    logger.info(f"Device: {DEVICE_NAME} | Endpoint: {AWS_IOT_ENDPOINT} | Topic: {MQTT_TOPIC}")
    logger.info(f"Mode: {'Real Sensor' if USE_REAL_SENSOR else 'Simulation'} | Send Interval: {SEND_INTERVAL}s")

    # Register signals for container-friendly lifecycle management
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    client = setup_mqtt()

    try:
        logger.info("Connecting to AWS IoT Core...")
        # AWS IoT Core MQTT standard secure port is 8883
        client.connect(AWS_IOT_ENDPOINT, port=8883, keepalive=60)
        client.loop_start()

        while running:
            data = read_sensors()
            if data is None:
                logger.warning("Sensor read failed, skipping this interval...")
                time.sleep(SEND_INTERVAL)
                continue

            payload_json = json.dumps(data)
            client.publish(MQTT_TOPIC, payload_json, qos=1)

            logger.info(
                f"Published telemetry: Temp={data['temperature']}°C, "
                f"Humi={data['humidity']}%, Press={data['pressure']} hPa"
            )

            # Sleep in small increments to respond quickly to shutdown signals
            for _ in range(SEND_INTERVAL):
                if not running:
                    break
                time.sleep(1)

    except Exception as e:
        logger.error(f"Run-time exception: {e}")
    finally:
        logger.info("Disconnecting MQTT client...")
        client.loop_stop()
        client.disconnect()
        logger.info("Publisher stopped cleanly.")

if __name__ == "__main__":
    main()
