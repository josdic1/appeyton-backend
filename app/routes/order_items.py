# app/routes/order_items.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderItemUpdate, OrderItemResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission
from app.utils import toast_responses

# main.py mounts this router at /api/order-items
# so DO NOT add prefix="/order-items" here.
router = APIRouter(tags=["Order Items"])


@router.patch("/{item_id}", response_model=OrderItemResponse)
def update_order_item(
    item_id: int,
    payload: OrderItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "write")),
):
    """Updates a specific item within an order (quantity, notes, etc.)."""
    item = (
        db.query(OrderItem)
        .options(
            joinedload(OrderItem.order).joinedload(Order.reservation),
            joinedload(OrderItem.menu_item),
            joinedload(OrderItem.attendee),
        )
        .filter(OrderItem.id == item_id)
        .first()
    )

    if not item:
        return toast_responses.error_not_found("Order Item", item_id)

    # Ownership Validation
    if scope == "own":
        res = item.order.reservation if item.order else None
        if not res or res.user_id != user.id:
            return toast_responses.error_forbidden("Order Item", "update")

    # Update fields
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)

    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "delete")),
):
    """Removes an item from an order."""
    item = (
        db.query(OrderItem)
        .options(joinedload(OrderItem.order).joinedload(Order.reservation))
        .filter(OrderItem.id == item_id)
        .first()
    )

    if not item:
        return toast_responses.error_not_found("Order Item", item_id)

    # Ownership Validation
    if scope == "own":
        res = item.order.reservation if item.order else None
        if not res or res.user_id != user.id:
            return toast_responses.error_forbidden("Order Item", "delete")

    db.delete(item)
    db.commit()
    return None
