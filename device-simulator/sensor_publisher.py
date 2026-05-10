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
import paho.mqtt.client as mqtt
from config import (
    AWS_IOT_ENDPOINT, MQTT_TOPIC, DEVICE_NAME,
    ROOT_CA, CERT_FILE, KEY_FILE, SEND_INTERVAL
)

# Set to True if running on real Raspberry Pi with DHT sensor
USE_REAL_SENSOR = False

if USE_REAL_SENSOR:
    import Adafruit_DHT
    SENSOR     = Adafruit_DHT.DHT22
    SENSOR_PIN = 17

# ── Sensor reading ────────────────────────────────
def read_sensors():
    """
    Read from real hardware OR simulate data.
    Every ~10th reading injects an anomaly to test alerts.
    """
    tick = getattr(read_sensors, "tick", 0) + 1
    read_sensors.tick = tick

    if USE_REAL_SENSOR:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, SENSOR_PIN)
        pressure = round(random.uniform(1000, 1020), 2)  # simulated
        if humidity is None or temperature is None:
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
            print("⚠️  [ANOMALY INJECTED] High temperature!")
        elif anomaly_type == "low_humi":
            humidity = round(random.uniform(5, 12), 2)
            print("⚠️  [ANOMALY INJECTED] Low humidity!")
        else:
            pressure = round(random.uniform(1085, 1100), 2)
            print("⚠️  [ANOMALY INJECTED] High pressure!")

    return {
        "device_id"  : DEVICE_NAME,
        "timestamp"  : datetime.datetime.utcnow().isoformat() + "Z",
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
        print("✅ Connected to AWS IoT Core!")
    else:
        print(f"❌ Connection failed. Code: {rc}")

def on_disconnect(client, userdata, rc):
    print(f"⚠️  Disconnected (rc={rc})")

# ── Setup MQTT ────────────────────────────────────
def setup_mqtt():
    client = mqtt.Client(client_id=DEVICE_NAME)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.tls_set(
        ca_certs    = ROOT_CA,
        certfile    = CERT_FILE,
        keyfile     = KEY_FILE,
        tls_version = ssl.PROTOCOL_TLSv1_2
    )
    return client

# ── Main ──────────────────────────────────────────
def main():
    print("🔬 IoT Anomaly Detection Publisher Starting...")
    print(f"   Device   : {DEVICE_NAME}")
    print(f"   Endpoint : {AWS_IOT_ENDPOINT}")
    print(f"   Topic    : {MQTT_TOPIC}")
    print(f"   Interval : {SEND_INTERVAL}s")
    print(f"   Mode     : {'Real Sensor' if USE_REAL_SENSOR else 'Simulation'}")
    print("─" * 50)

    client = setup_mqtt()

    try:
        print("🔌 Connecting to AWS IoT Core...")
        client.connect(AWS_IOT_ENDPOINT, port=8883, keepalive=60)
        client.loop_start()

        while True:
            data = read_sensors()
            if data is None:
                print("⚠️  Sensor read failed, skipping...")
                time.sleep(SEND_INTERVAL)
                continue

            payload_json = json.dumps(data)
            client.publish(MQTT_TOPIC, payload_json, qos=1)

            print(f"📊 [{data['timestamp']}]")
            print(f"   🌡️  Temperature : {data['temperature']}°C")
            print(f"   💧 Humidity    : {data['humidity']}%")
            print(f"   🔵 Pressure    : {data['pressure']} hPa")
            print(f"   📤 Published to: {MQTT_TOPIC}")
            print("─" * 50)

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Stopping publisher...")
        client.loop_stop()
        client.disconnect()
        print("✅ Disconnected cleanly.")

if __name__ == "__main__":
    main()
