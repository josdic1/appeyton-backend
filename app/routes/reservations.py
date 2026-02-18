# app/routes/reservations.py
from datetime import datetime, timezone
from time import time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.reservation import Reservation
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from app.schemas.toast import ToastResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission
from app.utils.query_helpers import apply_permission_filter
from app.utils.toast_responses import (
    success_booking, 
    error_table_taken, 
    error_not_found,
    error_validation
)

router = APIRouter()

# ── NEW: Availability Endpoint (Member Accessible) ──
@router.get("/availability")
def check_availability(
    date: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Public availability check. Returns simplified booking data 
    so the frontend can disable taken tables.
    """
    from datetime import date as date_cls
    try:
        target_date = date_cls.fromisoformat(date)
    except ValueError:
        raise HTTPException(400, "Invalid date format")

    reservations = db.query(Reservation).filter(
        Reservation.date == target_date,
        Reservation.status != "cancelled"
    ).all()

    # Return minimal info needed for the table picker
    return [
        {
            "table_id": r.table_id,
            "meal_type": r.meal_type,
            "status": r.status,
            "start_time": r.start_time,
            "end_time": r.end_time
        }
        for r in reservations
    ]

@router.post("", response_model=ToastResponse)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "write")),
):
    start = time()
    
    table = db.query(TableEntity).filter(TableEntity.id == payload.table_id).first()
    if not table: 
        return error_not_found("Table", payload.table_id)
    
    # Check party size against table capacity
    if payload.party_size and payload.party_size > table.seat_count:
        return error_validation(
            field="party_size", 
            issue=f"exceeds table capacity of {table.seat_count}",
            suggestion="Please select a larger table or reduce your party size."
        )

    # Check party size against member's guest allowance
    if payload.party_size and user.role == "member":
        max_allowed = user.guest_allowance + 1
        if payload.party_size > max_allowed:
            return error_validation(
                field="party_size",
                issue=f"exceeds your guest allowance of {user.guest_allowance} guests",
                suggestion=f"Your membership allows up to {user.guest_allowance} guests plus yourself ({max_allowed} total). Contact the club to request an increase."
            )

    try:
        reservation = Reservation(
            **payload.model_dump(),
            user_id=user.id,
            status="pending",
            created_by_user_id=user.id,
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        
        return success_booking(
            table_number=table.table_number,
            party_size=payload.party_size or table.seat_count,
            user_name=user.name,
            booking_date=payload.date,
            start_time=payload.start_time,
            meal_type=payload.meal_type,
            dining_room_name="Venue",
            reservation_id=reservation.id,
            elapsed_ms=int((time() - start) * 1000)
        )
    except IntegrityError:
        db.rollback()
        return error_table_taken(table.table_number, payload.date, payload.meal_type, [])


@router.get("", response_model=list[ReservationResponse])
def list_reservations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "read"))
):
    query = db.query(Reservation).options(joinedload(Reservation.attendees))
    return apply_permission_filter(query, Reservation, scope, user.id).all()


@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "write")),
):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r: 
        raise HTTPException(404)
    if scope == "own" and r.user_id != user.id: 
        raise HTTPException(403)

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "delete")),
):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r: 
        raise HTTPException(404)
    if scope == "own" and r.user_id != user.id: 
        raise HTTPException(403)
    db.delete(r)
    db.commit()
    return None