# app/models/dining_room.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.table_entity import TableEntity

# JSONB if Postgres; JSON otherwise
try:
    from sqlalchemy.dialects.postgresql import JSONB  # type: ignore
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType  # type: ignore


class DiningRoom(Base):
    __tablename__ = "dining_rooms"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Relationship to tables
    tables: Mapped[list["TableEntity"]] = relationship("TableEntity", back_populates="dining_room", lazy="select")
    
    @property
    def capacity(self) -> int:
        """Calculate capacity from sum of table seats"""
        return sum(table.seat_count for table in self.tables)