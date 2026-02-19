# app/models/dining_room.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Integer, ForeignKey, DateTime, JSON, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import Base

if TYPE_CHECKING:
    from app.models.table_entity import TableEntity

class DiningRoom(Base):
    __tablename__ = "dining_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    legal_capacity: Mapped[int] = mapped_column(
        Integer, default=100, server_default="100", nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        default=True, server_default="true", nullable=False
    )

    display_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Renamed db column to extra_data to avoid 'metadata' attribute confusion
    meta: Mapped[dict | None] = mapped_column("extra_data", JSON, nullable=True)

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

    tables: Mapped[List["TableEntity"]] = relationship(
        "TableEntity",
        back_populates="dining_room",
        cascade="all, delete-orphan",
        order_by="TableEntity.table_number",
    )

    @hybrid_property
    def setup_capacity(self) -> int:
        """Calculates total seats in Python."""
        return sum(table.seat_count for table in self.tables)

    @setup_capacity.inplace.expression
    @classmethod
    def _setup_capacity_expression(cls):
        """Allows SQL-side calculation of seat counts."""
        from app.models.table_entity import TableEntity
        return (
            select(func.sum(TableEntity.seat_count))
            .where(TableEntity.dining_room_id == cls.id)
            .label("setup_capacity")
            .scalar_subquery()
        )

    def __repr__(self) -> str:
        return f"<DiningRoom(name='{self.name}', capacity={self.setup_capacity}/{self.legal_capacity})>"