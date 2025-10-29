# scripts/producer_readings.py
import os, json, random, time, signal
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv()
BOOTSTRAP = os.getenv("BOOTSTRAP", "host.docker.internal:29092,host.docker.internal:29093")
TOPIC = os.getenv("TOPIC_READINGS", "iot.readings")
NUM_DEVICES = int(os.getenv("NUM_DEVICES", "100"))
INTERVAL_MS = int(os.getenv("SEND_INTERVAL_MS", "300"))

p = Producer({"bootstrap.servers": BOOTSTRAP, "linger.ms": 50, "acks": "all"})

running = True
def handle_sig(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, handle_sig)
signal.signal(signal.SIGTERM, handle_sig)

device_ids = [f"dev-{i:04d}" for i in range(NUM_DEVICES)]

def mk_reading(dev_id):
    base_f = 60 + (hash(dev_id) % 20)        # 60–79 °F baseline
    temp_f = round(random.gauss(base_f, 2.0), 2)
    hum_pct = round(random.uniform(25, 75), 2)
    # ISO8601 is optional; our consumer defaults to now() if missing
    ts_iso = None
    return dev_id, temp_f, hum_pct, ts_iso

print(f"🚀 Producing to {TOPIC} @ {BOOTSTRAP} (devices={NUM_DEVICES})")
while running:
    dev = random.choice(device_ids)
    dev, temp_f, hum_pct, ts = mk_reading(dev)

    msgs = [
        {"device_id": dev, "metric": "temperature_f", "value": temp_f, "ts": ts},
        {"device_id": dev, "metric": "humidity_pct",  "value": hum_pct, "ts": ts},
    ]
    for m in msgs:
        p.produce(TOPIC, key=dev.encode(), value=json.dumps(m).encode())
    p.poll(0)
    time.sleep(INTERVAL_MS / 1000.0)

print("⏳ Flushing…"); p.flush(5.0); print("✅ Producer exited cleanly")
