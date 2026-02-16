# app/utils/toast_responses.py
from __future__ import annotations

from datetime import datetime, date, time as time_type
from typing import Any, List, Optional

from fastapi.responses import JSONResponse

from app.schemas.toast import ActionButton, ToastResponse


class ToastJSONResponse(JSONResponse):
    """A JSONResponse that also exposes `.model_dump()` like a Pydantic model.

    This keeps backwards compatibility with code that calls:
        toast = error_not_found(...).model_dump()
    while allowing routes to return this object directly with the correct HTTP status.
    """

    def __init__(self, toast: ToastResponse, status_code: int):
        self.toast = toast
        super().__init__(status_code=status_code, content=toast.model_dump())

    def model_dump(self, *args, **kwargs):
        return self.toast.model_dump(*args, **kwargs)


def success_booking(
    table_number: int,
    party_size: int,
    user_name: str,
    booking_date: date,
    start_time: time_type,
    meal_type: str,
    dining_room_name: str,
    reservation_id: int,
    elapsed_ms: int,
) -> ToastJSONResponse:
    """Successful reservation booking (HTTP 201)."""
    toast = ToastResponse(
        status="success",
        what=f"Table {table_number} booked for {party_size} people",
        who=f"Reserved under your name: {user_name}",
        when=f"{booking_date.strftime('%a %b %d')}, {start_time.strftime('%I:%M%p')} {meal_type}",
        why="All validation passed, confirmation email sent",
        where=f"{dining_room_name}, {meal_type} service confirmed",
        how="Add to calendar or view full details",
        actions=[
            ActionButton(label="Add to Calendar", action="calendar", params={"reservation_id": reservation_id}),
            ActionButton(label="View Reservation", action="navigate", params={"view": f"/reservations/{reservation_id}"}),
            ActionButton(label="Add Attendees", action="navigate", params={"view": f"/reservations/{reservation_id}/attendees"}),
        ],
        meta={"response_time_ms": elapsed_ms, "reservation_id": reservation_id},
    )
    return ToastJSONResponse(toast, status_code=201)


def error_table_taken(
    table_num: int,
    booking_date: date,
    meal_type: str,
    alternatives: List[Any],
) -> ToastJSONResponse:
    """Table already booked (HTTP 409) - offer alternatives."""
    alt_actions = [
        ActionButton(label=f"Try Table {tbl_num}", action="retry", params={"table_id": tbl_id})
        for tbl_id, tbl_num in alternatives[:2]
    ]

    toast = ToastResponse(
        status="error",
        what=f"Table {table_num} already booked for that time",
        who="Another member reserved it seconds ago",
        when=f"{booking_date.strftime('%a %b %d')}, {meal_type} slot taken",
        why="Two people clicked Book at same time",
        where="This specific table is now fully booked",
        how="Try different time or pick nearby table",
        actions=alt_actions
        + [
            ActionButton(label="See All Available", action="navigate", params={"view": "/availability"}),
        ],
        meta={"alternatives_count": len(alternatives)},
    )
    return ToastJSONResponse(toast, status_code=409)


def error_not_found(resource: str, resource_id: Optional[int] = None) -> ToastJSONResponse:
    """Resource not found (HTTP 404)."""
    toast = ToastResponse(
        status="error",
        what=f"{resource} not found in system",
        who="May have been deleted by admin recently",
        when="Lookup failed during request processing",
        why="ID doesn't exist in database",
        where=f"Searching for {resource_id}" if resource_id else "Database lookup",
        how="Refresh page or contact support",
        actions=[
            ActionButton(label="Refresh", action="reload", params={}),
            ActionButton(label="Go Back", action="navigate", params={"view": "/"}),
        ],
    )
    return ToastJSONResponse(toast, status_code=404)


def error_unauthorized(required_role: str) -> ToastJSONResponse:
    """Unauthorized access attempt (HTTP 403)."""
    toast = ToastResponse(
        status="error",
        what="Access denied",
        who=f"Only {required_role} users allowed here now",
        when="Access level checked when request was made",
        why="Your account role doesn't allow this operation",
        where="This section requires higher permission level exactly",
        how="Contact admin to request access role upgrade",
        actions=[
            ActionButton(label="Go Home", action="navigate", params={"view": "/"}),
        ],
    )
    return ToastJSONResponse(toast, status_code=403)


def error_validation(field: str, issue: str, suggestion: str) -> ToastJSONResponse:
    """Validation error (HTTP 409 to match your reservation conflict semantics)."""
    toast = ToastResponse(
        status="error",
        what=f"Invalid {field}: {issue}",
        who="Your request had missing/invalid details",
        when="Validation failed before booking could proceed",
        why=f"{field} failed constraints check",
        where=f"Field: {field}",
        how=suggestion,
        actions=[ActionButton(label="Fix & Retry", action="dismiss", params={})],
        meta={"field": field, "issue": issue},
    )
    return ToastJSONResponse(toast, status_code=409)


def success_generic(message: str) -> ToastJSONResponse:
    """Generic success message (HTTP 200)."""
    toast = ToastResponse(
        status="success",
        what=message,
        who="Request completed successfully",
        when=datetime.now().strftime("%I:%M %p"),
        why="All operations completed without error",
        where="System backend processing",
        how="Continue with next step",
        actions=[ActionButton(label="Continue", action="dismiss", params={})],
    )
    return ToastJSONResponse(toast, status_code=200)


def error_server(details: str) -> ToastJSONResponse:
    """Internal server error (HTTP 500)."""
    toast = ToastResponse(
        status="error",
        what="Server error occurred",
        who="Our system hit an unexpected issue",
        when="During your request processing now",
        why="Unhandled exception in backend code",
        where="Internal server logic layer",
        how="Try again in 30 seconds or contact support",
        actions=[ActionButton(label="Retry", action="reload", params={})],
        meta={"details": details[:200]},
    )
    return ToastJSONResponse(toast, status_code=500)


def success_order_created(order_id: int, reservation_id: int) -> ToastJSONResponse:
    """Order created successfully (HTTP 201)."""
    toast = ToastResponse(
        status="success",
        what=f"Order #{order_id} placed successfully",
        who="Kitchen has received your order",
        when="Just now",
        why="All items were available and assigned",
        where=f"Reservation #{reservation_id}",
        how="Wait for staff confirmation",
        actions=[
            ActionButton(label="View Order", action="navigate", params={"view": f"/orders/{order_id}"}),
            ActionButton(label="Close", action="dismiss", params={}),
        ],
        meta={"order_id": order_id, "reservation_id": reservation_id},
    )
    return ToastJSONResponse(toast, status_code=201)


def error_menu_item_unavailable(item_name: str) -> ToastJSONResponse:
    """Menu item not available (HTTP 409)."""
    toast = ToastResponse(
        status="error",
        what=f"{item_name} is not available right now",
        who="Kitchen marked this item as unavailable today",
        when="Status checked just now when processing order",
        why="Item out of stock or not served",
        where="This specific menu item cannot be ordered",
        how="Choose different item from available menu options",
        actions=[ActionButton(label="View Menu", action="navigate", params={"view": "/menu"})],
    )
    return ToastJSONResponse(toast, status_code=409)
