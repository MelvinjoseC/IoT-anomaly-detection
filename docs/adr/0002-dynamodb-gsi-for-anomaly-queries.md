# 2. DynamoDB Global Secondary Index (GSI) for Anomaly Queries

Date: 2026-07-28

## Status
Accepted

## Context
The DynamoDB `SensorReadings` table uses `device_id` as the partition key and `timestamp` as the sort key. When engineers or operational dashboards query historical anomalies across all devices, the table required a full Table Scan. In production, as telemetry volume scales into millions of records, full table scans incur heavy read capacity unit costs and unacceptable latency.

## Decision
We introduced a Global Secondary Index named `AnomalyIndex`:
- Partition Key: `is_anomaly_idx` (String: `"TRUE"` / `"FALSE"`)
- Sort Key: `timestamp` (String ISO 8601)
- Projection: `ALL`

## Consequences
- Positive: Sub-second queries for recent anomalies ordered chronologically across all devices without scanning non-anomalous telemetry.
- Negative: Incremental write storage and write capacity consumption when anomalies occur.
