import os
import json
import signal
from collections import deque, defaultdict
from statistics import mean
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaException

# Load .env at project root
load_dotenv()
BOOTSTRAP = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("TOPIC", "iot.sensors")

GROUP_ID = "iot-stats-v3"   # bump version if you want a fresh group
WINDOW = int(os.getenv("WINDOW_SIZE", "20"))  # rolling window per device

def main():
    c = Consumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False #nough for Kafdrop to show the group
        # Optional: "debug": "broker,protocol,cgrp"
    })

    running = True
    def handle_sig(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    buffers = defaultdict(lambda: deque(maxlen=WINDOW))

    print(f"📈 Stats consumer connecting to {BOOTSTRAP}, topic={TOPIC}, group={GROUP_ID}, window={WINDOW}")
    c.subscribe([TOPIC])

    try:
        while running:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            data = json.loads(msg.value())
            dev = data["device_id"]
            temp = data["temperature_f"]
            buffers[dev].append(temp)

            if len(buffers[dev]) == WINDOW:
                avg_t = round(mean(buffers[dev]), 2)
                print(f"dev={dev} avg_last_{WINDOW}={avg_t}F")

    finally:
        c.close()
        print("✅ Stats consumer closed")

if __name__ == "__main__":
    main()
