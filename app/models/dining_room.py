from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Integer, ForeignKey, DateTime, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base
from app.models.table_entity import TableEntity

if TYPE_CHECKING:
    from app.models.user import User

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType

class DiningRoom(Base):
    __tablename__ = "dining_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Fire code limit
    legal_capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
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
    tables: Mapped[List["TableEntity"]] = relationship(
        "TableEntity", 
        back_populates="dining_room",
        cascade="all, delete-orphan",
        order_by="TableEntity.table_number"
    )

    @hybrid_property
    def setup_capacity(self) -> int:
        """Sum of all table seats currently in the room."""
        return sum(table.seat_count for table in self.tables) if self.tables else 0

    def __repr__(self) -> str:
        return f"<DiningRoom(name='{self.name}', capacity={self.setup_capacity}/{self.legal_capacity})>"