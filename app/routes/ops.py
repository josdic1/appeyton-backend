from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.models.seat import Seat
from app.utils.permissions import get_current_user, get_permission

from app.schemas.user_public import UserPublic
from app.schemas.reservation import ReservationResponse
from app.schemas.reservation_attendee import (
    ReservationAttendeeResponse, 
    ReservationAttendeeSyncList
)
from app.schemas.dining_room import DiningRoomResponse
from app.schemas.table_entity import TableEntityResponse
from app.schemas.seat import SeatResponse

router = APIRouter()

# ─── SYNC LOGIC (FOR EDITING PARTIES) ───

@router.patch("/reservations/{reservation_id}/attendees/sync", response_model=List[ReservationAttendeeResponse])
def ops_sync_attendees(
    reservation_id: int,
    payload: ReservationAttendeeSyncList,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "write")),
):
    """
    Reconciles the guest manifest.
    1. Updates existing guests (where ID matches).
    2. Creates new guests (where ID is missing).
    3. Deletes guests not present in the payload.
    """
    if scope != "all":
        raise HTTPException(status_code=403, detail="Staff access required for manifest sync")

    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    existing_guests = db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()
    
    existing_map = {g.id: g for g in existing_guests}
    incoming_ids = [a.id for a in payload.attendees if a.id is not None]
    
    # 1. DELETE removed guests
    for g_id, guest in existing_map.items():
        if g_id not in incoming_ids:
            db.delete(guest)

    # 2. UPDATE or CREATE
    for a in payload.attendees:
        if a.id and a.id in existing_map:
            # Update existing
            target = existing_map[a.id]
            for key, value in a.model_dump(exclude={'id', 'reservation_id'}).items():
                setattr(target, key, value)
        else:
            # Create new
            new_guest = ReservationAttendee(
                **a.model_dump(exclude={'id'}),
                reservation_id=reservation_id,
                created_by_user_id=user.id
            )
            db.add(new_guest)

    db.commit()
    return db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()


# ─── LISTING & READ ENDPOINTS ───

@router.get("/users", response_model=list[UserPublic])
def ops_list_users(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    """Staff view to list all users. Requires 'all' scope."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Staff access required for user directory")
    return db.query(User).order_by(User.id.desc()).all()


@router.get("/dining-rooms", response_model=list[DiningRoomResponse])
def ops_list_rooms(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "read")),
):
    return db.query(DiningRoom).order_by(DiningRoom.display_order.asc()).all()


@router.get("/tables", response_model=list[TableEntityResponse])
def ops_list_tables(
    dining_room_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "read")),
):
    """Staff view of all tables, filterable by room."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    q = db.query(TableEntity)
    if dining_room_id is not None:
        q = q.filter(TableEntity.dining_room_id == dining_room_id)
    return q.order_by(TableEntity.dining_room_id.asc(), TableEntity.table_number.asc()).all()


@router.get("/seats", response_model=list[SeatResponse])
def ops_list_seats(
    table_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "read")),
):
    """Staff view for FloorPlanPage seat population."""
    if scope not in ("all",):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    q = db.query(Seat)
    if table_id is not None:
        q = q.filter(Seat.table_id == table_id)
    return q.order_by(Seat.table_id, Seat.seat_number).all()


@router.get("/reservations", response_model=list[ReservationResponse])
def ops_list_reservations(
    date: str | None = Query(None, description="YYYY-MM-DD"),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "read")),
):
    """Staff dashboard view for managing all restaurant bookings."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Access denied")

    # FIX: Using selectinload for collections to prevent f405 ambiguous column crashes
    q = db.query(Reservation).options(
        joinedload(Reservation.table),
        selectinload(Reservation.attendees)
    )
    
    if status:
        q = q.filter(Reservation.status == status)
    if date:
        from datetime import date as date_type
        try:
            parsed_date = date_type.fromisoformat(date)
            q = q.filter(Reservation.date == parsed_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")
            
    return q.order_by(Reservation.date.desc(), Reservation.start_time.asc()).all()


@router.get("/reservations/{reservation_id}/attendees", response_model=list[ReservationAttendeeResponse])
def ops_get_attendees(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "read")),
):
    """Get all attendees for a specific reservation."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()


@router.get("/attendees", response_model=list[ReservationAttendeeResponse])
def ops_list_all_attendees(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "read")),
):
    """Required for FloorPlanPage to populate all seat bubbles."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Staff access required")

    return db.query(ReservationAttendee).all()