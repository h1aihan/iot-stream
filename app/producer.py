import os, json, random, time, signal, sys
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv()
BOOTSTRAP = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("TOPIC", "iot.sensors")
NUM_DEVICES = int(os.getenv("NUM_DEVICES", "100"))
INTERVAL_MS = int(os.getenv("SEND_INTERVAL_MS", "300"))

p = Producer({"bootstrap.servers": BOOTSTRAP, "linger.ms": 50, "acks": "all"})

running = True
def handle_sig(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, handle_sig)
signal.signal(signal.SIGTERM, handle_sig)

def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}", flush=True)

device_ids = [f"dev-{i:04d}" for i in range(NUM_DEVICES)]

def mk_reading(dev_id):
    # Simple correlated temps per device
    base = 60 + (hash(dev_id) % 20)  # 60–79 baseline
    temp = round(random.gauss(base, 2.0), 2)   # add noise
    hum  = round(random.uniform(25, 75), 2)
    ts   = int(time.time() * 1000)
    return {
        "device_id": dev_id,
        "ts": ts,
        "temperature_f": temp,
        "humidity_pct": hum,
        "site": f"site-{int(dev_id.split('-')[1]) % 5}"
    }

print(f"🚀 Producing to {TOPIC} @ {BOOTSTRAP} (devices={NUM_DEVICES})")
while running:
    dev = random.choice(device_ids)
    reading = mk_reading(dev)
    key = dev.encode()
    val = json.dumps(reading).encode()
    p.produce(TOPIC, key=key, value=val, on_delivery=delivery_report)
    p.poll(0)  # serve delivery callbacks
    time.sleep(INTERVAL_MS / 1000.0)

print("⏳ Flushing…")
p.flush(5.0)
print("✅ Producer exited cleanly")
