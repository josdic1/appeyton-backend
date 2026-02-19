# app/utils/toast_responses.py
from __future__ import annotations
from datetime import datetime, date, time as time_type, timezone
from typing import Any, List, Optional
from fastapi.responses import JSONResponse
from app.schemas.toast import ActionButton, ToastResponse

class ToastJSONResponse(JSONResponse):
    def __init__(self, toast: ToastResponse, status_code: int):
        self.toast = toast
        super().__init__(status_code=status_code, content=toast.model_dump())

    def model_dump(self, *args, **kwargs):
        return self.toast.model_dump(*args, **kwargs)

def error_validation(field: str, issue: str, suggestion: str) -> ToastJSONResponse:
    """Handles 400/409 validation conflicts with rich feedback."""
    toast = ToastResponse(
        status="error",
        what=f"Validation failed for {field}",
        who="System validator",
        when="Just now",
        why=issue,
        where=f"Field: {field}",
        how=suggestion,
        actions=[ActionButton(label="Got it", action="dismiss", params={})],
        meta={"field": field, "issue": issue}
    )
    return ToastJSONResponse(toast, status_code=400)

def error_table_taken(
    table_num: int,
    booking_date: date,
    meal_type: str,
    alternatives: List[Any],
) -> ToastJSONResponse:
    toast = ToastResponse(
        status="error",
        what=f"Table {table_num} is already taken",
        who="Another guest",
        when=f"{booking_date.strftime('%a %b %d')}, {meal_type}",
        why="Booking conflict",
        where="Floor Plan",
        how="Choose a different table or time",
        actions=[ActionButton(label="View Availability", action="navigate", params={"view": "/availability"})]
    )
    return ToastJSONResponse(toast, status_code=409)

def error_not_found(resource: str, resource_id: Optional[int] = None) -> ToastJSONResponse:
    toast = ToastResponse(
        status="error",
        what=f"{resource} not found",
        who="Database",
        when="Now",
        why="The ID does not exist",
        where="Lookup layer",
        how="Check the ID and try again",
        actions=[]
    )
    return ToastJSONResponse(toast, status_code=404)

def error_forbidden(entity: str, action: str) -> ToastJSONResponse:
    toast = ToastResponse(
        status="error",
        what="Access Denied",
        who="Security Service",
        when="Just now",
        why="Insufficient permissions",
        where=f"{entity}:{action}",
        how="Contact an admin for access",
        actions=[]
    )
    return ToastJSONResponse(toast, status_code=403)

def error_server(details: str) -> ToastJSONResponse:
    toast = ToastResponse(
        status="error",
        what="System Error",
        who="Backend",
        when="Runtime",
        why="An unhandled exception occurred",
        where="Server Logic",
        how="Retry in a moment",
        actions=[],
        meta={"error": details[:200]}
    )
    return ToastJSONResponse(toast, status_code=500)

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
    toast = ToastResponse(
        status="success",
        what=f"Table {table_number} booked",
        who=user_name,
        when=f"{booking_date} {start_time}",
        why="Confirmed",
        where=dining_room_name,
        how="Reservation stored",
        actions=[],
        meta={"id": reservation_id, "ms": elapsed_ms}
    )
    return ToastJSONResponse(toast, status_code=201)