from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)
    location = Column(String(128), nullable=True)
    kind = Column(String(32), nullable=True) # e.g., temp, vib, pressure


class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), index=True, nullable=False)
    ts = Column(DateTime(timezone=True), server_default=text("now()"), index=True)
    value = Column(Float, nullable=False)
    metric = Column(String(32), nullable=False) # e.g., temperature


Index("ix_readings_device_metric_ts", Reading.device_id, Reading.metric, Reading.ts.desc())


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), index=True, nullable=False)
    ts = Column(DateTime(timezone=True), server_default=text("now()"), index=True)
    severity = Column(String(16), nullable=False) # info|warn|crit
    code = Column(String(32), nullable=False) # e.g., HIGH_TEMP
    message = Column(String(256), nullable=False)
    raw_key = Column(String(64), nullable=True)
    raw_partition = Column(Integer, nullable=True)
    raw_offset = Column(Integer, nullable=True)


Index("ix_alerts_device_ts", Alert.device_id, Alert.ts.desc())