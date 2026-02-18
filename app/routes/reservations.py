# app/routes/reservations.py
from datetime import datetime, timezone, date as date_obj
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.table_entity import TableEntity
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from app.models.user import User
from app.utils.permissions import get_current_user

router = APIRouter()

@router.get("/availability")
def check_availability(date: str = Query(...), db: Session = Depends(get_db)):
    try:
        parsed_date = date_obj.fromisoformat(date)
        return db.query(Reservation).filter(
            Reservation.date == parsed_date, 
            Reservation.status != "cancelled"
        ).all()
    except Exception:
        raise HTTPException(status_code=500, detail="Availability lookup failed")

@router.get("", response_model=list[ReservationResponse])
def list_reservations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Optimized loader to prevent f405 Ambiguous Column crashes.
    """
    return db.query(Reservation).options(
        joinedload(Reservation.table),      # For 1-to-1
        selectinload(Reservation.attendees), # Efficient for lists [cite: 2026-02-18]
        selectinload(Reservation.messages)   # Efficient for lists [cite: 2026-02-18]
    ).filter(Reservation.user_id == user.id).all()

@router.post("", response_model=ReservationResponse)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    table = db.query(TableEntity).filter(TableEntity.id == payload.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    try:
        new_res = Reservation(
            user_id=user.id,
            dining_room_id=payload.dining_room_id,
            table_id=payload.table_id,
            date=payload.date,
            meal_type=payload.meal_type,
            start_time=payload.start_time,
            end_time=payload.end_time,
            notes=payload.notes,
            status="confirmed",
            created_by_user_id=user.id
        )
        db.add(new_res)
        db.flush() 

        for a in payload.attendees:
            new_guest = ReservationAttendee(
                reservation_id=new_res.id,
                name=a.name,
                attendee_type=a.attendee_type,
                dietary_restrictions=a.dietary_restrictions,
                created_by_user_id=user.id
            )
            db.add(new_guest)

        db.commit()
        db.refresh(new_res)
        return new_res
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(reservation_id: int, payload: ReservationUpdate, db: Session = Depends(get_db)):
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    update_data = payload.model_dump(exclude_unset=True)

    # 1. INTEGRITY CHECK: Ensure table/room match [cite: 2026-02-18]
    if "table_id" in update_data or "dining_room_id" in update_data:
        new_room = update_data.get("dining_room_id", res.dining_room_id)
        new_table = update_data.get("table_id", res.table_id)
        table_verify = db.query(TableEntity).filter(
            TableEntity.id == new_table,
            TableEntity.dining_room_id == new_room
        ).first()
        if not table_verify:
            raise HTTPException(status_code=400, detail="Table/Room mismatch")

    # 2. AUTO-STAMP FIRE TIME (FIXES KDS TIMING) [cite: 2026-02-18]
    if update_data.get("status") == "fired" and res.status != "fired":
        res.fired_at = datetime.now(timezone.utc)

    for key, value in update_data.items():
        setattr(res, key, value)
    
    db.commit()
    db.refresh(res)
    return res