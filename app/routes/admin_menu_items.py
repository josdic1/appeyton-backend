# app/routes/admin_menu_items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_min_role("admin")),
):
    """Create a new menu item (admin only)"""
    item = MenuItem(
        name=payload.name,
        description=payload.description,
        category=payload.category,
        price=payload.price,
        is_available=payload.is_available,
        dietary_tags=payload.dietary_tags,
        display_order=payload.display_order,
        created_by_user_id=admin.id,
        updated_by_user_id=admin.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_min_role("admin")),
):
    """Update a menu item (admin only)"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)

    item.updated_by_user_id = admin.id

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_min_role("admin")),
):
    """Delete a menu item (admin only)"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(item)
    db.commit()
    return None