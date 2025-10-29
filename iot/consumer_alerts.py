import os
import json
import signal
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaException

# Load .env at project root
load_dotenv()
BOOTSTRAP = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("TOPIC", "iot.sensors")

GROUP_ID = "iot-alerts-v3"  # bump version if you want a fresh group

def main():
    c = Consumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit":False,   # let Kafka commit automatically
        # Optional: uncomment for verbose troubleshooting
        # "debug": "broker,protocol,cgrp"
    })

    running = True
    def handle_sig(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    print(f"🛎️  Alerts consumer connecting to {BOOTSTRAP}, topic={TOPIC}, group={GROUP_ID}")
    c.subscribe([TOPIC])

    try:
        while running:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            data = json.loads(msg.value())
            temp = data["temperature_f"]
            dev  = data["device_id"]
            site = data.get("site", "n/a")

            if temp > 80:
                print(f"🔥 ALERT: {dev} @ {site} HIGH temp={temp}F ts={data['ts']}")
            elif temp < 55:
                print(f"❄️ ALERT: {dev} @ {site} LOW temp={temp}F ts={data['ts']}")

    finally:
        c.close()
        print("✅ Alerts consumer closed")

if __name__ == "__main__":
    main()
