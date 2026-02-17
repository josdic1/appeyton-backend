# app/routes/admin_dining_rooms.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dining_room import DiningRoom
from app.schemas.dining_room import DiningRoomCreate, DiningRoomUpdate, DiningRoomResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.post("", response_model=DiningRoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: DiningRoomCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_min_role("admin")),
):
    room = DiningRoom(
        name=payload.name,
        is_active=payload.is_active,
        display_order=payload.display_order,
        meta=payload.meta,
        created_by_user_id=admin.id,
        updated_by_user_id=admin.id,
    )
    db.add(room)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Dining room name already exists")

    db.refresh(room)
    return room


@router.patch("/{room_id}", response_model=DiningRoomResponse)
def update_room(
    room_id: int,
    payload: DiningRoomUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_min_role("admin")),
):
    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(room, k, v)

    room.updated_by_user_id = admin.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Dining room name already exists")

    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_min_role("admin")),
):
    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")

    db.delete(room)
    db.commit()
    return None