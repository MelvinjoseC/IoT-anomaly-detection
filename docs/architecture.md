# 📐 Architecture — IoT Anomaly Detection System

## Data Flow

```
┌──────────────────────────────────────┐
│  ESP32 / Raspberry Pi / Simulator    │
│  (Dockerized Non-root / Mock Mode)   │
│  Reads: Temp, Humidity, Pressure     │
└──────────────────┬───────────────────┘
                   │ MQTT over TLS (Port 8883)
                   │ Topic: sensors/environment
                   ▼
┌──────────────────────────────────────┐
│  AWS IoT Core                        │
│  • X.509 mutual auth                 │
│  • Topic Rule: sensors/environment   │
└─────────┬──────────────────┬─────────┘
          │ Invoke           │ Error / Throttle Action
          ▼                  ▼
┌──────────────────┐  ┌──────────────────────────────────────┐
│   AWS Lambda     │  │  AWS SQS Dead-Letter Queue (DLQ)     │
│  (IoTAnomaly-    │  │  • 14-day encrypted retention        │
│   Detector)      │  │  • Alarm on visible messages         │
│  • X-Ray Tracing │  └──────────────────┬───────────────────┘
│  • JSON logging  │                     ▲
└─┬──────────────┬─┘                     │ Asynchronous Redrive
  │              │                       │
  │ Anomaly      │ Always (All Data)     │
  ▼              ▼                       │
┌──────────────┐ ┌─────────────────────────┴────────┐
│   AWS SNS    │ │  AWS DynamoDB (SensorReadings)    │
│  • Encrypted │ │  • PK: device_id, SK: timestamp  │
│  • Email/SMS │ │  • GSI: AnomalyIndex             │
│    alerts    │ │  • TTL Auto-cleanup (30 Days)     │
└──────────────┘ └───────────────────────────────────┘
       ▲                          ▲
       │                          │
┌──────┴──────────────────────────┴─────────────────┐
│  Centralized Observability & Reliability           │
│  • CloudWatch Operational Dashboard as Code       │
│  • Metric Alarms: Errors, Throttles, Latency, DLQ  │
│  • AWS X-Ray Distributed End-to-End Tracing       │
└───────────────────────────────────────────────────┘
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
