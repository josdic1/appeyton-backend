# app/models/member.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)

    # The User account this member belongs to
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # The User (likely staff) who created this member record
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), 
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    relation: Mapped[str | None] = mapped_column(String(60), nullable=True)

    dietary_restrictions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Changed column name to 'extra_data' to avoid 'metadata' collision
    meta: Mapped[dict | None] = mapped_column("extra_data", JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships - specifying foreign_keys is required because there are two links to 'users'
    owner: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id], 
        backref="family_members"
    )
    
    creator: Mapped["User | None"] = relationship(
        "User", 
        foreign_keys=[created_by_user_id]
    )

    def __repr__(self) -> str:
        return f"<Member(name='{self.name}', relation='{self.relation}')>"