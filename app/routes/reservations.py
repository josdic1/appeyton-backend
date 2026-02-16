# app/routes/reservations.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.reservation import Reservation
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


def _assert_table_exists(
    db: Session,
    dining_room_id: int,
    table_id: int,
):
    room = db.query(DiningRoom).filter(DiningRoom.id == dining_room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    if not room.is_active:
        raise HTTPException(status_code=409, detail="Dining room is not active")

    table = (
        db.query(TableEntity)
        .filter(TableEntity.id == table_id, TableEntity.dining_room_id == dining_room_id)
        .first()
    )
    if not table:
        raise HTTPException(status_code=404, detail="Table not found in that dining room")
    
    return table


# app/routes/reservations.py
from time import time
from sqlalchemy.exc import IntegrityError
from app.schemas.toast import ToastResponse
from app.utils.toast_responses import (
    success_booking, 
    error_table_taken, 
    error_not_found,
    error_validation
)

@router.post("", response_model=ToastResponse)  # ← Changed from ReservationResponse
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """
    Create a new reservation.
    
    Now returns structured toast response with actionable guidance.
    """
    start = time()
    
    # Validate dining room exists
    dining_room = db.query(DiningRoom).filter(
        DiningRoom.id == payload.dining_room_id
    ).first()
    if not dining_room:
        return error_not_found("Dining room", payload.dining_room_id)
    
    # Validate table exists
    table = db.query(TableEntity).filter(
        TableEntity.id == payload.table_id
    ).first()
    if not table:
        return error_not_found("Table", payload.table_id)
    
    # Validate party size
    if payload.party_size and payload.party_size > table.seat_count:
        return error_validation(
            field="party_size",
            issue=f"exceeds table capacity of {table.seat_count}",
            suggestion=f"Choose table with {payload.party_size}+ seats available"
        )
    
    try:
        # Create reservation
        reservation = Reservation(
            user_id=user.id,
            dining_room_id=payload.dining_room_id,
            table_id=payload.table_id,
            date=payload.date,
            meal_type=payload.meal_type,
            start_time=payload.start_time,
            end_time=payload.end_time,
            party_size=payload.party_size,
            notes=payload.notes,
            status="pending",
            created_by_user_id=user.id,
        )
        
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        
        elapsed = int((time() - start) * 1000)
        
        return success_booking(
            table_number=table.table_number,
            party_size=payload.party_size or table.seat_count,
            user_name=user.name,
            booking_date=payload.date,
            start_time=payload.start_time,
            meal_type=payload.meal_type,
            dining_room_name=dining_room.name,
            reservation_id=reservation.id,
            elapsed_ms=elapsed
        )
        
    except IntegrityError:
        db.rollback()
        
        # Find alternative tables in same room
        alternatives = db.query(TableEntity.id, TableEntity.table_number).filter(
            TableEntity.dining_room_id == payload.dining_room_id,
            TableEntity.seat_count >= (payload.party_size or 1),
            ~TableEntity.id.in_(
                db.query(Reservation.table_id).filter(
                    Reservation.date == payload.date,
                    Reservation.meal_type == payload.meal_type,
                    Reservation.status.in_(["pending", "confirmed"])
                )
            )
        ).limit(3).all()
        
        return error_table_taken(
            table_num=table.table_number,
            booking_date=payload.date,
            meal_type=payload.meal_type,
            alternatives=alternatives
        )


@router.get("", response_model=list[ReservationResponse])
def list_my_reservations(
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Members see only their own reservations"""
    return (
        db.query(Reservation)
        .options(joinedload(Reservation.attendees))
        .filter(Reservation.user_id == user.id)
        .order_by(Reservation.date.desc(), Reservation.start_time.desc())
        .all()
    )


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    r = (
        db.query(Reservation)
        .options(joinedload(Reservation.attendees))
        .filter(Reservation.id == reservation_id, Reservation.user_id == user.id)
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return r


@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    r = (
        db.query(Reservation)
        .options(joinedload(Reservation.attendees))
        .filter(Reservation.id == reservation_id, Reservation.user_id == user.id)
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")

    data = payload.model_dump(exclude_unset=True)

    dining_room_id = data.get("dining_room_id", r.dining_room_id)
    table_id = data.get("table_id", r.table_id)

    table = _assert_table_exists(db, dining_room_id, table_id)
    
    # Check if party size (attendees) exceeds table capacity
    if len(r.attendees) > table.seat_count:
        raise HTTPException(
            status_code=409, 
            detail=f"Cannot update: {len(r.attendees)} attendees exceed table capacity of {table.seat_count}"
        )

    for k, v in data.items():
        setattr(r, k, v)

    if "status" in data:
        if data["status"] == "confirmed":
            r.confirmed_at = datetime.now(timezone.utc)
        if data["status"] == "cancelled":
            r.cancelled_at = datetime.now(timezone.utc)
            r.cancelled_by_user_id = user.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="That table is already booked for that date+meal_type")

    db.refresh(r)
    return r


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    r = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.user_id == user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(r)
    db.commit()
    return None