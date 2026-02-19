# app/models/audit_trail.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Dict, Any

from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .user import User

class AuditTrail(Base):
    """Complete change history for all tables with before/after snapshots"""
    __tablename__ = "audit_trails"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Target table and specific row ID
    table_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    record_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Action type: INSERT, UPDATE, DELETE
    operation: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Who did it?
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    
    # Snapshot of the data
    old_values: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # List of keys that were actually modified
    changed_fields: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Optional: Contextual info (use sparingly to save space)
    sql_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return (f"<AuditTrail(table='{self.table_name}', "
                f"id={self.record_id}, op='{self.operation}')>")