# backend/db.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load .env from repo root
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

def _default_db_url():
    if Path("/.dockerenv").exists() or os.getenv("RUN_IN_DOCKER") == "1":
        host = "postgres"
    else:
        host = "localhost"
    return f"postgresql+psycopg2://iot:iotpw@{host}:5432/iotdb"

DB_URL = os.getenv("DB_URL", _default_db_url())

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
