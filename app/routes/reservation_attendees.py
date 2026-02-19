# app/routes/reservation_attendees.py
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.user import User
from app.schemas.reservation_attendee import (
    ReservationAttendeeResponse,
    ReservationAttendeeSyncList,
)
from app.utils.auth import get_current_user
from app.utils.permissions import get_permission
from app.utils import toast_responses

# IMPORTANT:
# main.py already provides the prefix: /api/reservation-attendees
# So this router MUST NOT add another "/reservation-attendees" prefix.
router = APIRouter(tags=["reservation-attendees"])


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
    - Deletes removed attendees.
    - Upserts by attendee ID when provided.
    - If member_id is present, normalizes from Member.
    """
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        return toast_responses.error_not_found("Reservation", reservation_id)

    # Ownership validation
    if scope == "own" and res.user_id != user.id:
        return toast_responses.error_forbidden("ReservationAttendee", "sync")

    existing = (
        db.query(ReservationAttendee)
        .filter(ReservationAttendee.reservation_id == reservation_id)
        .all()
    )
    existing_map = {a.id: a for a in existing}

    incoming_ids = [a.id for a in payload.attendees if a.id]

    # 1) Delete removed attendees
    for attendee_id, attendee in existing_map.items():
        if attendee_id not in incoming_ids:
            db.delete(attendee)

    updated_list: List[ReservationAttendee] = []

    # 2) Upsert incoming attendees
    for a_data in payload.attendees:
        data = a_data.model_dump(exclude_unset=True)

        member_id = data.get("member_id")

        if member_id is not None:
            member_obj = db.query(Member).filter(Member.id == member_id).first()
            if not member_obj:
                return toast_responses.error_validation(
                    field="member_id",
                    issue="Profile not found.",
                    suggestion="Select a valid family member.",
                )

            # Member must belong to the reservation owner
            if getattr(member_obj, "user_id", None) != res.user_id:
                return toast_responses.error_forbidden("Member", "link_to_reservation")

            # Normalize from member profile
            data.setdefault("name", member_obj.name)
            data["attendee_type"] = "member"
            if data.get("dietary_restrictions") is None:
                data["dietary_restrictions"] = getattr(member_obj, "dietary_restrictions", None)
        else:
            # Guest attendee
            data.setdefault("attendee_type", "guest")
            if not data.get("name"):
                return toast_responses.error_validation(
                    field="name",
                    issue="Guest requires a name.",
                    suggestion="Enter the name of your guest.",
                )

        # Strip keys we don't allow updating this way
        target_id = data.pop("id", None)
        data.pop("reservation_id", None)

        if target_id and target_id in existing_map:
            attendee = existing_map[target_id]
            for key, value in data.items():
                setattr(attendee, key, value)
        else:
            attendee = ReservationAttendee(
                reservation_id=reservation_id,
                created_by_user_id=user.id,
                **data,
            )
            db.add(attendee)

        updated_list.append(attendee)

    try:
        db.commit()
        for a in updated_list:
            db.refresh(a)
        return updated_list
    except Exception as e:
        db.rollback()
        return toast_responses.error_server(f"Sync failed: {str(e)}")
