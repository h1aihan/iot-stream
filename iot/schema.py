from pydantic import BaseModel
from typing import Optional


class IoTReading(BaseModel):
    device_id: str
    metric: str # e.g., "temperature"
    value: float
    ts: Optional[str] = None # ISO8601, optional; default to now in consumer if missing


class IoTAlert(BaseModel):
    device_id: str
    code: str # e.g., "HIGH_TEMP"
    severity: str # info|warn|crit
    message: str
    ts: Optional[str] = None