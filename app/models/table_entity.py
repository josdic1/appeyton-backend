from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB  # type: ignore
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType  # type: ignore


class TableEntity(Base):
    __tablename__ = "table_entities"
    __table_args__ = (
        UniqueConstraint("dining_room_id", "table_number", name="uq_table_room_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    dining_room_id: Mapped[int] = mapped_column(ForeignKey("dining_rooms.id"), nullable=False, index=True)
    table_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False)

    position_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int | None] = mapped_column(Integer, nullable=True)

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
