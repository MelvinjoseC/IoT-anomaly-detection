# 📐 Architecture — IoT Anomaly Detection System

## Data Flow

```
┌──────────────────────────┐
│  ESP32 / Raspberry Pi     │
│                           │
│  Reads every 5 seconds:   │
│  • Temperature (°C)       │
│  • Humidity (%)           │
│  • Pressure (hPa)         │
└────────────┬─────────────┘
             │ MQTT over TLS
             │ Topic: sensors/environment
             ▼
┌──────────────────────────┐
│  AWS IoT Core             │
│  • X.509 auth             │
│  • IoT Rule fires         │
│    on every message       │
└────────────┬─────────────┘
             │ Invoke Lambda directly
             ▼
┌──────────────────────────┐
│  AWS Lambda               │
│  IoTAnomalyDetector       │
│                           │
│  For each reading:        │
│  1. Validate fields       │
│  2. Check thresholds:     │
│     Temp: 10–40°C         │
│     Humi: 15–90%          │
│     Pres: 950–1080 hPa    │
│  3. If anomaly → SNS      │
│  4. Always → DynamoDB     │
└──────┬──────────┬────────┘
       │          │
       │ anomaly  │ always
       ▼          ▼
┌──────────┐  ┌──────────────────┐
│ AWS SNS  │  │  AWS DynamoDB     │
│          │  │  SensorReadings   │
│ Sends:   │  │                   │
│ 📧 Email │  │  Stores:          │
│ 📱 SMS   │  │  • All readings   │
└──────────┘  │  • is_anomaly flag│
              │  • anomaly_types  │
              │  • alert_sent     │
              └──────────────────┘

     ↕ monitors
┌──────────────────────────┐
│  AWS CloudWatch           │
│  • Lambda error rate      │
│  • Invocation count       │
│  • Alarm if errors > 5    │
└──────────────────────────┘
```

## Anomaly Detection Logic

```python
# Simple threshold-based detection
if temperature > 40 or temperature < 10:
    → ANOMALY: HIGH/LOW TEMPERATURE

if humidity > 90 or humidity < 15:
    → ANOMALY: HIGH/LOW HUMIDITY

if pressure > 1080 or pressure < 950:
    → ANOMALY: HIGH/LOW PRESSURE
```

## Why This Matters in Production

Real-world uses of this exact pattern:
- Factory floor temperature monitoring
- Cold chain logistics (medicines/food)
- Server room environment monitoring
- Industrial equipment health monitoring
- Drone/UAV environmental sensing

This pattern — IoT → Lambda → SNS alert — is used by
companies like Amazon warehouses, hospitals, and data centers.
