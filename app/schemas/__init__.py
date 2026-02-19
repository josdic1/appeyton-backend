# app/schemas/__init__.py
from __future__ import annotations

# Auth & User Schemas
from .user import (
    UserCreate,
    UserUpdate,
    UserAdminUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
)
from .user_public import UserPublic
from .ops import UserOpsResponse

# Dining & Floor Plan Schemas
from .dining_room import DiningRoomCreate, DiningRoomUpdate, DiningRoomResponse
from .table_entity import TableEntityCreate, TableEntityUpdate, TableEntityResponse
from .seat import SeatCreate, SeatUpdate, SeatResponse

# Reservation & Guest Schemas
from .reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from .reservation_attendee import (
    ReservationAttendeeCreate,
    ReservationAttendeeUpdate,
    ReservationAttendeeResponse,
    ReservationAttendeeSyncList,
)
from .member import MemberCreate, MemberUpdate, MemberResponse
from .reservation_message import ReservationMessageCreate, ReservationMessageResponse

# Order & Menu Schemas
from .menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from .order import (
    OrderItemCreate, 
    OrderItemUpdate, 
    OrderItemResponse, 
    OrderCreate, 
    OrderUpdate, 
    OrderResponse, 
    OrderWithItemsResponse
)

# Financial & Admin Schemas
from .reservation_total import ReservationTotalResponse
from .notification import NotificationCreate, NotificationResponse
from .toast import ToastResponse, ActionButton

# System & Reporting Schemas (New placeholders we discussed)
from .activity_log import ActivityLogResponse
from .daily_stat import DailyStatResponse

# This allows you to control exactly what is exported when someone does 'from app.schemas import *'
__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserAdminUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "UserPublic",
    "UserOpsResponse",
    "DiningRoomCreate",
    "DiningRoomUpdate",
    "DiningRoomResponse",
    "TableEntityCreate",
    "TableEntityUpdate",
    "TableEntityResponse",
    "SeatCreate",
    "SeatUpdate",
    "SeatResponse",
    "ReservationCreate",
    "ReservationUpdate",
    "ReservationResponse",
    "ReservationAttendeeCreate",
    "ReservationAttendeeUpdate",
    "ReservationAttendeeResponse",
    "ReservationAttendeeSyncList",
    "MemberCreate",
    "MemberUpdate",
    "MemberResponse",
    "ReservationMessageCreate",
    "ReservationMessageResponse",
    "MenuItemCreate",
    "MenuItemUpdate",
    "MenuItemResponse",
    "OrderItemCreate",
    "OrderItemUpdate",
    "OrderItemResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderWithItemsResponse",
    "ReservationTotalResponse",
    "NotificationCreate",
    "NotificationResponse",
    "ToastResponse",
    "ActionButton",
    "ActivityLogResponse",
    "DailyStatResponse",
]