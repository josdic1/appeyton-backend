# app/routes/menu_items.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.models.user import User
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.utils.permissions import require_min_role

router = APIRouter()

@router.get("", response_model=list[MenuItemResponse])
def list_menu_items(
    category: str | None = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    query = db.query(MenuItem)
    if category:
        query = query.filter(MenuItem.category == category)
    if available_only:
        query = query.filter(MenuItem.is_available == True)
    return query.order_by(MenuItem.category, MenuItem.display_order, MenuItem.name).all()

@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.post("", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    item_in: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role("admin")),
):
    item = MenuItem(**item_in.model_dump(), created_by_user_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_in: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role("admin")),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for field, val in item_in.model_dump(exclude_unset=True).items():
        setattr(item, field, val)
    item.updated_by_user_id = current_user.id
    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("admin")),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()