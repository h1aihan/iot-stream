import json
from datetime import datetime, timezone
from confluent_kafka import Consumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from iot.schema import IoTReading
from backend.models import Base, Reading
from iot.config import BOOTSTRAP, DB_URL, TOPIC_READINGS

import logging
from iot.config import BOOTSTRAP, DB_URL, TOPIC_READINGS
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logging.info(f"[stats] BOOTSTRAP={BOOTSTRAP}  DB_URL={DB_URL}  TOPIC={TOPIC_READINGS}")

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)


c = Consumer({
"bootstrap.servers": BOOTSTRAP,
"group.id": "iot.readings.g1",
"auto.offset.reset": "earliest",
"enable.auto.commit": True,
})


c.subscribe([TOPIC_READINGS])
print("[readings] consuming…")

try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Kafka error:", msg.error())
            continue
        try:
            payload = json.loads(msg.value())
            data = IoTReading(**payload)
            ts = datetime.fromisoformat(data.ts) if data.ts else datetime.now(timezone.utc)
            with SessionLocal() as db:
                db.add(Reading(device_id=data.device_id, metric=data.metric, value=data.value, ts=ts))
                db.commit()
        except Exception as e:
            print("parse/insert error:", e)
finally:
        c.close()