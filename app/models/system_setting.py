# app/models/system_setting.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class SystemSetting(Base):
    """Key/value store for app-wide configuration.
    
    Used for: permissions matrix, feature flags, any runtime config
    that needs to survive deploys.
    """
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # The unique name of the setting (e.g., 'MAINTENANCE_MODE')
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # The actual configuration data
    value: Mapped[Dict[str, Any] | Any | None] = mapped_column(JSON, nullable=True)

    # Added to provide context for what this setting controls
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit Trail
    updated_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )

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
    updater: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<SystemSetting(key='{self.key}', value={self.value})>"