# app/models/seat.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, UniqueConstraint, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.table_entity import TableEntity
    from app.models.user import User

class Seat(Base):
    """Individual seats at tables - for optional seat assignments."""
    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("table_id", "seat_number", name="uq_seat_table_seat_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    table_id: Mapped[int] = mapped_column(
        ForeignKey("table_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[str | None] = mapped_column(String(50), nullable=True) # e.g., "Window side"

    is_accessible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    # Simplified JSON: SQLAlchemy handles JSONB automatically on Postgres
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit Trail
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    table: Mapped["TableEntity"] = relationship("TableEntity", back_populates="seats")
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_user_id])
    updater: Mapped["User | None"] = relationship("User", foreign_keys=[updated_by_user_id])

    def __repr__(self) -> str:
        return f"<Seat(table_id={self.table_id}, number={self.seat_number}, accessible={self.is_accessible})>"