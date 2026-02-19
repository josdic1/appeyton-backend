from __future__ import annotations
from datetime import datetime, timezone, date as date_obj
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.table_entity import TableEntity
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from app.utils.auth import get_current_user
from app.utils.permissions import get_permission
from app.utils.query_helpers import apply_permission_filter
from app.utils import toast_responses

router = APIRouter(tags=["reservations"])

@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "write")),
):
    booking_date: date_obj = payload.date or payload.reservation_time.date()
    meal_type: str = payload.meal_type or "Dinner"
    start_time = payload.start_time or payload.reservation_time.time()
    
    if payload.table_id:
        table = db.query(TableEntity).filter(TableEntity.id == payload.table_id).first()
        if not table:
            return toast_responses.error_not_found("Table", payload.table_id)

    try:
        # 1. Create Primary Reservation (REMOVED party_size assignment)
        new_res = Reservation(
            user_id=user.id,
            dining_room_id=payload.dining_room_id,
            table_id=payload.table_id,
            date=booking_date,
            meal_type=meal_type,
            start_time=start_time,
            end_time=payload.end_time or start_time,
            notes=payload.notes,
            status="confirmed",
            created_by_user_id=user.id,
        )
        
        db.add(new_res)
        db.flush() 

        # 2. Create Attendee Rows (This drives the @property party_size)
        for a in payload.attendees:
            db.add(
                ReservationAttendee(
                    reservation_id=new_res.id,
                    name=a.name or "Guest",
                    attendee_type=a.attendee_type or "member",
                    dietary_restrictions=a.dietary_restrictions,
                    created_by_user_id=user.id,
                )
            )

        db.commit()
        db.refresh(new_res)

        # 3. Reload with relationships
        created = (
            db.query(Reservation)
            .options(
                joinedload(Reservation.table),
                selectinload(Reservation.attendees),
                selectinload(Reservation.messages),
            )
            .filter(Reservation.id == new_res.id)
            .first()
        )
        return created

    except Exception as e:
        db.rollback()
        return toast_responses.error_server(str(e))

@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "write")),
):
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        return toast_responses.error_not_found("Reservation", reservation_id)
    if scope == "own" and res.user_id != user.id:
        return toast_responses.error_forbidden("Reservation", "write")

    update_data = payload.model_dump(exclude_unset=True)
    update_data.pop("party_size", None) # Safety: Never try to update party_size directly

    if update_data.get("status") == "fired" and res.status != "fired":
        res.fired_at = datetime.now(timezone.utc)

    for key, value in update_data.items():
        setattr(res, key, value)

    db.commit()
    db.refresh(res)
    return res