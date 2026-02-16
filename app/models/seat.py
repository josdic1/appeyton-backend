# app/models/seat.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.table_entity import TableEntity

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class Seat(Base):
    """Individual seats at tables - for specific seat assignments (OPTIONAL)"""
    __tablename__ = "seats"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    table_id: Mapped[int] = mapped_column(
        ForeignKey("table_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # seat_number: 1, 2, 3, etc. relative to the table
    
    position: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # position: "head", "foot", "left", "right", "corner"
    
    is_accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # is_accessible: True if wheelchair accessible
    
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    preferences: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    # preferences: {"view": "window", "near": "kitchen", "quiet": true}
    
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    table: Mapped["TableEntity"] = relationship("TableEntity")


# If you want to track who sits where, add to ReservationAttendee:
# seat_id: Mapped[int | None] = mapped_column(ForeignKey("seats.id"), nullable=True)

# Example Seats:
# Table 1 (4 seats):
#   - Seat 1: position="head", is_accessible=False
#   - Seat 2: position="left", is_accessible=False  
#   - Seat 3: position="right", is_accessible=True
#   - Seat 4: position="foot", is_accessible=False