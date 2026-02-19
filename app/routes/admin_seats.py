# app/routes/admin_seats.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.seat import Seat
from app.schemas.seat import SeatResponse
from app.utils.permissions import get_permission
from app.utils import toast_responses

# IMPORTANT:
# main.py mounts this router at /api/admin/seats
# so DO NOT add prefix="/admin/seats" here.
router = APIRouter(tags=["Admin - Seats"])


@router.get("", response_model=List[SeatResponse])
def list_seats(
    db: Session = Depends(get_db),
    scope: str = Depends(get_permission("Seat", "read")),
):
    """Admin view of all physical seats."""
    if scope == "none":
        return toast_responses.error_forbidden("Seat", "read")

    return (
        db.query(Seat)
        .order_by(Seat.table_id.asc(), Seat.seat_number.asc())
        .all()
    )
