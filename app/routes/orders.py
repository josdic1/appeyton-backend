# app/routes/orders.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.reservation import Reservation
from app.models.menu_item import MenuItem
from app.schemas.order import OrderCreate, OrderWithItemsResponse
from app.utils.auth import get_current_user
from app.utils.permissions import get_permission
from app.utils import toast_responses

# main.py mounts this router at /api/orders
# so DO NOT add prefix="/orders" here.
router = APIRouter(tags=["Orders"])


# ── READ OPERATIONS ──────────────────────────────────────────────────

@router.get("/by-reservation/{reservation_id}", response_model=OrderWithItemsResponse)
def get_order_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "read")),
):
    """Fetches the current tab/order for a specific reservation."""
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items).joinedload(OrderItem.menu_item),
            joinedload(Order.items).joinedload(OrderItem.attendee),
        )
        .filter(Order.reservation_id == reservation_id)
        .first()
    )

    if not order:
        return toast_responses.error_not_found("Order", reservation_id)

    # Ownership check for members
    if scope == "own":
        res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not res or res.user_id != user.id:
            return toast_responses.error_forbidden("Order", "read")

    return order


# ── WRITE OPERATIONS ─────────────────────────────────────────────────

@router.post("", response_model=OrderWithItemsResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "write")),
):
    """
    Creates an order shell if missing and appends items.
    Uses historical pricing from MenuItem at the time of order.
    """
    # 1) Validate Reservation
    res = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not res:
        return toast_responses.error_not_found("Reservation", payload.reservation_id)

    if scope == "own" and res.user_id != user.id:
        return toast_responses.error_forbidden("Order", "write")

    # 2) Get or Create Order Shell
    order = db.query(Order).filter(Order.reservation_id == res.id).first()
    if not order:
        order = Order(
            reservation_id=res.id,
            status="incomplete",
            created_by_user_id=user.id,
        )
        db.add(order)
        db.flush()  # get order.id

    # 3) Process Items
    for item_in in payload.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_in.menu_item_id).first()
        if not menu_item:
            # Better to validate, but keeping your current behavior:
            continue

        new_item = OrderItem(
            order_id=order.id,
            menu_item_id=item_in.menu_item_id,
            reservation_attendee_id=item_in.reservation_attendee_id,
            quantity=item_in.quantity,
            unit_price=menu_item.price,  # capture historical price
            special_instructions=item_in.special_instructions,
        )
        db.add(new_item)

    try:
        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        return toast_responses.error_server(f"Failed to process order: {str(e)}")

    return order
