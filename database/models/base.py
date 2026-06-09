import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    ENGINE = create_engine(DATABASE_URL)
else:
    DB_FILE = Path(__file__).resolve().parent.parent.parent / "database.db"
    ENGINE = create_engine(f"sqlite:///{DB_FILE}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

BASE = declarative_base()


def create_db():
    BASE.metadata.create_all(bind=ENGINE)

