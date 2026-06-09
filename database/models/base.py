from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DB_FILE = Path(__file__).resolve().parent.parent.parent / "database.db"

ENGINE = create_engine(f"sqlite:///{DB_FILE}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

BASE = declarative_base()


def create_db():
    BASE.metadata.create_all(bind=ENGINE)
