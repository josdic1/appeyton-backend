# ── FIX: Add a '#' to the start of the first line or delete it ──
# app/routes/reservation_attendees.py 

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.reservation_attendee import ReservationAttendeeSyncList, ReservationAttendeeResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

# This variable MUST be named router for main.py to find it [cite: 2026-02-18]
router = APIRouter()

@router.patch("/sync/{reservation_id}", response_model=List[ReservationAttendeeResponse])
def sync_attendees(
    reservation_id: int,
    payload: ReservationAttendeeSyncList,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "write")),
):
    """
    Reconciles the guest manifest.
    Prevents 'Nuke and Pave' by matching IDs to keep food orders safe. [cite: 2026-02-18]
    """
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(404, "Reservation not found")
    
    if scope == "own" and res.user_id != user.id:
        raise HTTPException(403, "Not authorized")

    existing_guests = db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()
    existing_map = {g.id: g for g in existing_guests}
    
    new_guest_ids = [a.id for a in payload.attendees if a.id]

    # DELETE: Only remove those not in the new list [cite: 2026-02-18]
    for gid, guest in existing_map.items():
        if gid not in new_guest_ids:
            db.delete(guest)

    # UPSERT: Match by ID or create new [cite: 2026-02-18]
    updated_list = []
    for a_data in payload.attendees:
        if a_data.id and a_data.id in existing_map:
            guest = existing_map[a_data.id]
            for key, value in a_data.model_dump(exclude_unset=True).items():
                setattr(guest, key, value)
        else:
            guest = ReservationAttendee(
                reservation_id=reservation_id,
                created_by_user_id=user.id,
                **a_data.model_dump(exclude={"reservation_id", "id"})
            )
            db.add(guest)
        updated_list.append(guest)

    db.commit()
    for g in updated_list:
        db.refresh(g)
    return updated_list