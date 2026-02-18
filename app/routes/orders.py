# app/routes/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.reservation import Reservation
from app.models.menu_item import MenuItem
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderWithItemsResponse,
)
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()


@router.post("", response_model=OrderWithItemsResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "write")),
):
    reservation = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if scope == "own" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    # Upsert: if order already exists, replace items for the attendees in payload
    existing_order = db.query(Order).filter(Order.reservation_id == reservation.id).first()
    if existing_order:
        # If payload items is explicitly empty, maybe we don't want to wipe everything?
        # But assuming "save order" means "this is the current state":
        if payload.items:
            attendee_ids = {item.reservation_attendee_id for item in payload.items}
            db.query(OrderItem).filter(
                OrderItem.order_id == existing_order.id,
                OrderItem.reservation_attendee_id.in_(attendee_ids),
            ).delete(synchronize_session=False)
        order = existing_order
    else:
        order = Order(reservation_id=reservation.id, status="incomplete", notes=payload.notes)
        db.add(order)
        db.flush()

    if payload.items:
        for item_in in payload.items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item_in.menu_item_id).first()
            if not menu_item:
                db.rollback()
                raise HTTPException(status_code=404, detail=f"Menu item {item_in.menu_item_id} not found")
            
            # Check availability if desired
            if not menu_item.is_available:
                 db.rollback()
                 raise HTTPException(status_code=409, detail=f"{menu_item.name} is not available")

            attendee = db.query(ReservationAttendee).filter(
                ReservationAttendee.id == item_in.reservation_attendee_id,
                ReservationAttendee.reservation_id == reservation.id,
            ).first()
            if not attendee:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Attendee {item_in.reservation_attendee_id} not found on this reservation"
                )

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_in.menu_item_id,
                reservation_attendee_id=item_in.reservation_attendee_id,
                quantity=item_in.quantity,
                unit_price=menu_item.price,
                special_instructions=item_in.special_instructions,
            )
            db.add(order_item)

    db.commit()
    db.refresh(order)
    return order


# ── CRITICAL FIX: Missing endpoint added here ──
@router.get("/by-reservation/{reservation_id}", response_model=OrderWithItemsResponse)
def get_order_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "read")),
):
    """Fetch the order (with items) for a given reservation. 404 if none exists yet."""
    # Check reservation ownership first
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if scope == "own" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    order = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.reservation))
        .filter(Order.reservation_id == reservation_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="No order for this reservation")

    return order


@router.get("/{order_id}", response_model=OrderWithItemsResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "read")),
):
    order = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.reservation))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if scope == "own" and order.reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")

    return order


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "write")),
):
    order = db.query(Order).options(joinedload(Order.reservation)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if scope == "own" and order.reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(order, k, v)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "delete")),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if scope != "all":
        raise HTTPException(status_code=403, detail="Only admins can delete full orders")
    db.delete(order)
    db.commit()
    return None