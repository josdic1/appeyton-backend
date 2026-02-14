# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# Production-ready Postgres connection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Test connections before using
    pool_size=5,                 # Keep 5 connections in pool
    max_overflow=10,             # Allow 10 extra connections if needed
    echo=False,                  # Set to True for SQL debug logging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()