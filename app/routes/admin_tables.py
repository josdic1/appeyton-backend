# app/routes/admin_tables.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.table_entity import TableEntity
from app.schemas.table_entity import TableEntityCreate, TableEntityUpdate, TableEntityResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[TableEntityResponse])
def list_tables(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_min_role("admin")),
):
    return (
        db.query(TableEntity)
        .order_by(TableEntity.dining_room_id.asc(), TableEntity.table_number.asc())
        .all()
    )


@router.post("", response_model=TableEntityResponse, status_code=status.HTTP_201_CREATED)
def create_table(
    payload: TableEntityCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_min_role("admin")),
):
    t = TableEntity(
        dining_room_id=payload.dining_room_id,
        table_number=payload.table_number,
        seat_count=payload.seat_count,
        position_x=payload.position_x,
        position_y=payload.position_y,
        meta=payload.meta,
        created_by_user_id=admin.id,
        updated_by_user_id=admin.id,
    )
    db.add(t)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Table number already exists in that dining room")

    db.refresh(t)
    return t


@router.patch("/{table_id}", response_model=TableEntityResponse)
def update_table(
    table_id: int,
    payload: TableEntityUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_min_role("admin")),
):
    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)

    t.updated_by_user_id = admin.id

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
    _admin: User = Depends(require_min_role("admin")),
):
    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(t)
    db.commit()
    return None