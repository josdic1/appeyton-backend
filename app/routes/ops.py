# app/routes/ops.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.utils.permissions import require_min_role

from app.schemas.user_public import UserPublic
from app.schemas.reservation import ReservationResponse
from app.schemas.reservation_attendee import ReservationAttendeeResponse
from app.schemas.dining_room import DiningRoomResponse
from app.schemas.table_entity import TableEntityResponse

router = APIRouter()

@router.get("/users", response_model=list[UserPublic])
def ops_list_users(
    db: Session = Depends(get_db),
    _staff: User = Depends(require_min_role("staff")),
):
    # no email/phone in schema
    return db.query(User).order_by(User.id.desc()).all()

@router.get("/dining-rooms", response_model=list[DiningRoomResponse])
def ops_list_rooms(
    db: Session = Depends(get_db),
    _staff: User = Depends(require_min_role("staff")),
):
    return db.query(DiningRoom).order_by(DiningRoom.display_order.asc(), DiningRoom.id.asc()).all()

@router.get("/tables", response_model=list[TableEntityResponse])
def ops_list_tables(
    dining_room_id: int | None = Query(None),
    db: Session = Depends(get_db),
    _staff: User = Depends(require_min_role("staff")),
):
    q = db.query(TableEntity)
    if dining_room_id is not None:
        q = q.filter(TableEntity.dining_room_id == dining_room_id)
    return q.order_by(TableEntity.dining_room_id.asc(), TableEntity.table_number.asc()).all()

@router.get("/reservations", response_model=list[ReservationResponse])
def ops_list_reservations(
    date: str | None = Query(None, description="YYYY-MM-DD"),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _staff: User = Depends(require_min_role("staff")),
):
    q = db.query(Reservation)
    if status:
        q = q.filter(Reservation.status == status)
    if date:
        q = q.filter(Reservation.date == date)
    return q.order_by(Reservation.date.desc(), Reservation.start_time.asc()).all()

@router.get("/reservations/{reservation_id}/attendees", response_model=list[ReservationAttendeeResponse])
def ops_list_attendees(
    reservation_id: int,
    db: Session = Depends(get_db),
    _staff: User = Depends(require_min_role("staff")),
):
    return (
        db.query(ReservationAttendee)
        .filter(ReservationAttendee.reservation_id == reservation_id)
        .order_by(ReservationAttendee.id.asc())
        .all()
    )
