# 4. AWS X-Ray Distributed Tracing

Date: 2026-07-30

## Status
Accepted

## Context
Diagnosing latency regressions across IoT Core, Lambda cold starts, DynamoDB write latencies, and SNS delivery times required correlation across disparate CloudWatch logs.

## Decision
We enabled AWS X-Ray Active Tracing (`mode = "Active"`) on the Lambda function and granted required least-privilege IAM permissions (`xray:PutTraceSegments`, `xray:PutTelemetryRecords`). The Lambda code includes auto-patching hooks for the AWS X-Ray SDK.

## Consequences
- Positive: Visual service map and latency distribution graphs in AWS X-Ray console.
- Positive: Immediate identification of downstream bottlenecks (e.g. DynamoDB partition throttling or SNS publish latency).
