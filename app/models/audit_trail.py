# app/models/audit_trail.py
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class AuditTrail(Base):
    """Complete change history for all tables with before/after snapshots"""
    __tablename__ = "audit_trails"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    record_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    old_values: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    changed_fields: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    
    sql_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Example usage:
    # table_name: "reservations"
    # record_id: 123
    # operation: "UPDATE"
    # old_values: {"status": "pending"}
    # new_values: {"status": "confirmed"}
    # changed_fields: ["status"]