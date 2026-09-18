# Multi-stage hardened lightweight Dockerfile for the IoT Device Simulator
FROM python:3.14-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final production stage
FROM python:3.14-slim

LABEL org.opencontainers.image.title="IoT Device Simulator" \
      org.opencontainers.image.description="Simulates IoT environmental telemetry and anomaly generation for AWS IoT Core" \
      org.opencontainers.image.authors="Melvin Chacko Jose <melvinjose025@gmail.com>" \
      org.opencontainers.image.source="https://github.com/MelvinjoseC/IoT-anomaly-detection" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Create non-root system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy installed python dependencies from builder stage
COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup . .

ENV PYTHONUNBUFFERED=1

# Container health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import sensor_publisher; exit(0 if sensor_publisher.running else 1)" || exit 1

# Drop to non-root user
USER appuser

CMD ["python", "sensor_publisher.py"]

