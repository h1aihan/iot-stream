🛰️ IoT Stream App

A lightweight real-time data pipeline showing how IoT sensors send data through Kafka, get processed by Python consumers, and stored in Postgres for analysis.

💡 Overview

The project simulates a modern industrial or energy monitoring system — like how smart-grid devices report status and alerts in real time.

Flow:
Producer → Kafka → Consumer → Postgres → (Dashboard / API)

🧱 Architecture
Layer	Purpose	Tools
Producers	Send sensor data (JSON)	Python scripts / Kafka CLI
Message Bus	Stream data reliably	Kafka (2 brokers) + Zookeeper
Consumers	Process and store data	Python (aiokafka, asyncpg)
Storage & UI	Persist and inspect	Postgres + Adminer + Redpanda Console
⚙️ Run Locally
# start containers
docker compose up -d

# create topic
docker compose exec broker1 kafka-topics --bootstrap-server broker1:9092 \
  --create --topic iot.alerts --partitions 3 --replication-factor 2

# send sample messages
docker compose exec -i broker1 kafka-console-producer \
  --broker-list broker1:9092 --topic iot.alerts
{"sensor_id":"S-001","ts":"2025-10-28T00:00:00Z","level":"INFO","msg":"boot"}
{"sensor_id":"S-002","ts":"2025-10-28T00:00:05Z","level":"WARN","msg":"temp high"}


View data

Kafka: Redpanda Console
 → iot.alerts

DB: Adminer
 → login with

User: iot

Password: iotpw

DB: iotdb

🧠 Current Status

✅ Multi-broker Kafka cluster running
✅ Postgres + Adminer ready
✅ Redpanda Console for visualization

Next: implement consumer_alerts.py to store alerts in Postgres.
Future: add stats consumer + FastAPI dashboard.

👨‍💻 Author

Han Hai — exploring IoT and smart-energy data systems.