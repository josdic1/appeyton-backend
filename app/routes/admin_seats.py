# app/routes/admin_seats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.seat import Seat
from app.schemas.seat import SeatResponse
from app.utils.permissions import get_permission

router = APIRouter()


@router.get("", response_model=list[SeatResponse])
def list_seats(
    db: Session = Depends(get_db),
    scope: str = Depends(get_permission("Seat", "read")),
):
    return db.query(Seat).order_by(Seat.table_id, Seat.seat_number).all()