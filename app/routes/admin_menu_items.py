from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()

@router.get("", response_model=list[MenuItemResponse])
def list_menu_items(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")
    return db.query(MenuItem).order_by(MenuItem.category, MenuItem.display_order, MenuItem.name).all()


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")
    
    item = MenuItem(
        **payload.model_dump(),
        created_by_user_id=user.id,
        updated_by_user_id=user.id,
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
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)

    item.updated_by_user_id = user.id
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "delete")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(item)
    db.commit()
    return None