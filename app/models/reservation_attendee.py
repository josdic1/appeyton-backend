from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB  # type: ignore
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType  # type: ignore


class ReservationAttendee(Base):
    __tablename__ = "reservation_attendees"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    attendee_type: Mapped[str] = mapped_column(String(30), nullable=False)  # member/guest/staff/etc

    dietary_restrictions: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
