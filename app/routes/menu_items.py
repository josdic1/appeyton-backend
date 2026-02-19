# app/routes/menu_items.py
from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.models.order_item import OrderItem
from app.models.user import User
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.utils.auth import get_current_user
from app.utils.permissions import get_permission
from app.utils import toast_responses

# IMPORTANT:
# main.py already provides the prefix: /api/menu-items
# So this router MUST NOT add another "/menu-items" prefix.
router = APIRouter(tags=["menu-items"])

# ── READ ─────────────────────────────────────────────────────────────

@router.get("/grouped", response_model=Dict[str, List[MenuItemResponse]])
def get_grouped_menu(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    """Returns available items grouped by category."""
    if scope == "none":
        return toast_responses.error_forbidden("MenuItem", "read")

    items = (
        db.query(MenuItem)
        .filter(MenuItem.is_available == True)  # noqa: E712
        .order_by(MenuItem.category, MenuItem.display_order, MenuItem.name)
        .all()
    )

    grouped: Dict[str, List[MenuItem]] = {}
    for item in items:
        cat = (item.category or "Other").strip()
        key = cat.capitalize() if cat else "Other"
        grouped.setdefault(key, []).append(item)

    return grouped


@router.get("", response_model=List[MenuItemResponse])
def list_menu_items(
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    """List endpoint with optional availability filtering."""
    if scope == "none":
        return toast_responses.error_forbidden("MenuItem", "read")

    query = db.query(MenuItem)
    if available_only:
        query = query.filter(MenuItem.is_available == True)  # noqa: E712

    return query.order_by(MenuItem.category, MenuItem.display_order, MenuItem.name).all()


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    """Fetch a specific menu item."""
    if scope == "none":
        return toast_responses.error_forbidden("MenuItem", "read")

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return toast_responses.error_not_found("Menu Item", item_id)
    return item

# ── WRITE (Admin/Staff depending on your permission matrix) ──────────

@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "write")),
):
    if scope != "all":
        return toast_responses.error_forbidden("MenuItem", "write")

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
        return toast_responses.error_forbidden("MenuItem", "write")

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return toast_responses.error_not_found("Menu Item", item_id)

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
        return toast_responses.error_forbidden("MenuItem", "delete")

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return toast_responses.error_not_found("Menu Item", item_id)

    has_orders = db.query(OrderItem).filter(OrderItem.menu_item_id == item_id).first()
    if has_orders:
        return toast_responses.error_server(
            "Conflict: This item is linked to existing orders. Mark it 'unavailable' instead of deleting."
        )

    db.delete(item)
    db.commit()
    return None
