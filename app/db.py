from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.POSTGRES_DSN, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

def init_db() -> None:
    from . import models  # noqa: F401 ensure models are imported
    Base.metadata.create_all(bind=engine)