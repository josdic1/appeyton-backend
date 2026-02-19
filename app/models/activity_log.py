# app/models/activity_log.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .user import User

class ActivityLog(Base):
    """Track all user actions in the system"""
    __tablename__ = "activity_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key to the user who performed the action
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    
    # e.g., "create", "update", "cancel_reservation"
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # e.g., "reservation", "order", "menu_item"
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # ID of the resource (not a formal FK to allow for polymorphism)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Contextual data (diffs, error messages, etc.)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Network info for security auditing
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ActivityLog(user_id={self.user_id}, action='{self.action}', resource='{self.resource_type}')>"