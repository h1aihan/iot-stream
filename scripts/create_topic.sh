#!/usr/bin/env bash
set -euo pipefail

TOPIC=${1:-iot.sensors}
PARTITIONS=${2:-6}
REPL=${3:-2}

docker compose exec broker1 kafka-topics \
  --create \
  --topic "$TOPIC" \
  --bootstrap-server broker1:9092,broker2:9092 \
  --partitions "$PARTITIONS" \
  --replication-factor "$REPL" || true

docker compose exec broker1 kafka-topics \
  --describe \
  --topic "$TOPIC" \
  --bootstrap-server broker1:9092,broker2:9092
