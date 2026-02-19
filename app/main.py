import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from alembic.config import Config
from alembic import command
from contextlib import asynccontextmanager

from app.routes import (
    users, members, reservations, reservation_attendees,
    dining_rooms, menu_items, orders, order_items,
    admin_tables, admin_menu_items,
    admin_users, admin_seats, ops,
    reservation_messages, notifications
)
from app.utils.toast_responses import error_server

def run_migrations() -> None:
    """Syncs the database schema to the latest Alembic head."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(base_dir, "alembic.ini")
    alembic_cfg = Config(ini_path)
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations synced to head.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("RUN_MIGRATIONS", "1") == "1":
        run_migrations()
    yield

app = FastAPI(
    title="Sterling Catering API", 
    redirect_slashes=False,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)

# -- Simplified Route Registration --
# Each router is included ONCE with its functional prefix.

# Users & Auth -> /api/users/login, /api/users/me, etc.
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# Core Resources
app.include_router(members.router, prefix="/api/members", tags=["Members"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["Reservations"])
app.include_router(reservation_attendees.router, prefix="/api/reservation-attendees", tags=["Attendees"])
app.include_router(reservation_messages.router, prefix="/api/reservation-messages", tags=["Messages"])
app.include_router(dining_rooms.router, prefix="/api/dining-rooms", tags=["Dining Rooms"])
app.include_router(menu_items.router, prefix="/api/menu-items", tags=["Menu"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(order_items.router, prefix="/api/order-items", tags=["Order Items"])

# Admin & Ops
app.include_router(admin_tables.router, prefix="/api/admin/tables", tags=["Admin - Tables"])
app.include_router(admin_seats.router, prefix="/api/admin/seats", tags=["Admin - Seats"])
app.include_router(admin_menu_items.router, prefix="/api/admin/menu-items", tags=["Admin - Menu"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["Admin - Users"])
app.include_router(ops.router, prefix="/api/ops", tags=["Operations"])

@app.get("/")
def root():
    return {"message": "Sterling Catering API Operational"}

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    details = f"{type(exc).__name__}: {exc}"
    logging.error(f"🔥 500 Error on {request.method} {request.url}: {details}")
    return error_server(details)