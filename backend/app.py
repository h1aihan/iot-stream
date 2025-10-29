from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone


from .db import SessionLocal, engine
from .models import Base, Reading, Alert


Base.metadata.create_all(bind=engine)


app = FastAPI(title="IoT Backend API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/alerts/latest")
async def latest_alerts(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(Alert.ts.desc()).limit(limit).all()
    return [
    {
    "id": r.id,
    "device_id": r.device_id,
    "ts": r.ts.isoformat() if r.ts else None,
    "severity": r.severity,
    "code": r.code,
    "message": r.message,
    }
    for r in rows
    ]


@app.get("/readings/series")
async def readings_series(device_id: str, metric: str, hours: int = 6, db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - relativedelta(hours=hours)
    rows = (
        db.query(Reading)
        .filter(Reading.device_id == device_id, Reading.metric == metric, Reading.ts >= since)
        .order_by(Reading.ts.asc())
        .all()
        )
    return [{"t": r.ts.isoformat(), "v": r.value} for r in rows]


@app.get("/readings/agg")
async def readings_agg(metric: str, window: str = "1 hour", db: Session = Depends(get_db)):
# simple rolling avg per device using PostgreSQL time bucketing via date_trunc
    from sqlalchemy import text
    sql = text(
        """
    SELECT device_id,
    date_trunc(:window, ts) AS bucket,
    avg(value) AS avg_v,
    min(value) AS min_v,
    max(value) AS max_v,
    count(*) AS n
    FROM readings
    WHERE metric = :metric
    GROUP BY device_id, bucket
    ORDER BY device_id, bucket
    """
    )
    rows = db.execute(sql, {"metric": metric, "window": window}).fetchall()
    return [dict(r._mapping) for r in rows]