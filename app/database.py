# app/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# Naming convention for constraints (makes Alembic migrations much easier)
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Production-ready Postgres connection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Test connections before using
    pool_size=5,                 # Minimum connections to keep open
    max_overflow=10,             # Peak capacity
    pool_recycle=3600,           # Refresh connections hourly
    pool_timeout=30,             # Seconds to wait for a free connection
    echo=False,                  # Set to True for SQL debug logging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    """Base class for all models"""
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)

def get_db():
    """
    Dependency for FastAPI routes.
    Ensures that the DB session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()