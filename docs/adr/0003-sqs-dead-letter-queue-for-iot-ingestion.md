# 3. SQS Dead-Letter Queue (DLQ) for Ingestion Reliability

Date: 2026-07-29

## Status
Accepted

## Context
AWS IoT Core Rules invoke AWS Lambda asynchronously or synchronously. If Lambda encounters throttling, concurrency exhaustion, or unhandled runtime exceptions, the telemetry data would be silently discarded by IoT Core.

## Decision
We implemented a dedicated SQS Dead-Letter Queue (`iot-anomaly-dead-letter-queue`) with:
1. `error_action` configured on the IoT Core topic rule routing failed messages to SQS with a 14-day retention.
2. Lambda asynchronous invocation `dead_letter_config` targeting the same SQS DLQ.
3. Dedicated CloudWatch Metric Alarm `AnomalyDLQMessagesVisible` alerting on-call engineers when messages enter the queue.

## Consequences
- Positive: Zero telemetry loss under traffic spikes, concurrency limits, or temporary downstream outages. Messages can be replayed after incident resolution.
- Positive: Real-time alerting via CloudWatch alarm when dead letters appear.
