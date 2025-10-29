# iot/config.py
import os
from pathlib import Path

# Auto-load .env from repo root (one level up from this file)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

def _default_db_url():
    # If running inside a Docker container, use 'postgres' hostname; otherwise localhost
    if Path("/.dockerenv").exists() or os.getenv("RUN_IN_DOCKER") == "1":
        host = "postgres"
    else:
        host = "localhost"
    return f"postgresql+psycopg2://iot:iotpw@{host}:5432/iotdb"

# Kafka
BOOTSTRAP = os.getenv("BOOTSTRAP", "host.docker.internal:29092,host.docker.internal:29093")
GROUP_ALERTS = os.getenv("GROUP_ALERTS", "iot.alerts.g1")
TOPIC_ALERTS = os.getenv("TOPIC_ALERTS", "iot.alerts")
TOPIC_READINGS = os.getenv("TOPIC_READINGS", "iot.readings")

# Database
DB_URL = os.getenv("DB_URL", _default_db_url())
