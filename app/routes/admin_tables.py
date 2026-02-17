# app/routes/admin_tables.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.table_entity import TableEntity
from app.models.seat import Seat
from app.schemas.table_entity import TableEntityCreate, TableEntityUpdate, TableEntityResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()


@router.get("", response_model=list[TableEntityResponse])
def list_tables(
    db: Session = Depends(get_db),
    scope: str = Depends(get_permission("Table", "read")),
):
    return db.query(TableEntity).order_by(
        TableEntity.dining_room_id.asc(), TableEntity.table_number.asc()
    ).all()


@router.post("", response_model=TableEntityResponse, status_code=status.HTTP_201_CREATED)
def create_table(
    payload: TableEntityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    t = TableEntity(
        **payload.model_dump(),
        created_by_user_id=user.id,
        updated_by_user_id=user.id,
    )
    db.add(t)
    try:
        db.flush()  # get t.id without committing
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Table number already exists in that dining room")

    # Auto-generate Seat records — one per seat_count
    # Positions cycle for visual layout: top, right, bottom, left, then repeating
    POSITIONS = ["top", "right", "bottom", "left", "top-right", "bottom-right", "bottom-left", "top-left"]
    for i in range(payload.seat_count):
        seat = Seat(
            table_id=t.id,
            seat_number=i + 1,
            position=POSITIONS[i % len(POSITIONS)],
            is_accessible=False,
            is_available=True,
            created_by_user_id=user.id,
            updated_by_user_id=user.id,
        )
        db.add(seat)

    db.commit()
    db.refresh(t)
    return t


@router.patch("/{table_id}", response_model=TableEntityResponse)
def update_table(
    table_id: int,
    payload: TableEntityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")

    old_seat_count = t.seat_count

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)

    t.updated_by_user_id = user.id

    # If seat_count changed, sync Seat records
    if payload.seat_count is not None and payload.seat_count != old_seat_count:
        existing_seats = db.query(Seat).filter(Seat.table_id == table_id).order_by(Seat.seat_number).all()
        current_count = len(existing_seats)
        new_count = payload.seat_count

        if new_count > current_count:
            # Add missing seats
            POSITIONS = ["top", "right", "bottom", "left", "top-right", "bottom-right", "bottom-left", "top-left"]
            for i in range(current_count, new_count):
                seat = Seat(
                    table_id=table_id,
                    seat_number=i + 1,
                    position=POSITIONS[i % len(POSITIONS)],
                    is_accessible=False,
                    is_available=True,
                    created_by_user_id=user.id,
                    updated_by_user_id=user.id,
                )
                db.add(seat)
        elif new_count < current_count:
            # Remove excess seats (highest seat numbers first, safest)
            seats_to_remove = existing_seats[new_count:]
            for seat in seats_to_remove:
                db.delete(seat)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Table number already exists in that dining room")

    db.refresh(t)
    return t


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "delete")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(t)
    db.commit()
    return None