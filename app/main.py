# app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from alembic.config import Config
from alembic import command

# Import Routers
from app.routes import (
    users, 
    members, 
    reservations, 
    reservation_attendees,
    dining_rooms, 
    menu_items, 
    orders, 
    order_items,
    admin_dining_rooms, 
    admin_tables, 
    admin_menu_items,
    admin_users, 
    admin_seats, 
    ops,
    reservation_messages, # New
    notifications         # New
)
from app.utils.toast_responses import error_server

# 1. Database Migration Logic
def run_migrations():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ini_path = os.path.join(base_dir, "alembic.ini")
        alembic_cfg = Config(ini_path)
        alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations synced to head.")
    except Exception as e:
        print(f"⚠️ Migration skipping or error: {e}")

run_migrations()

# 2. App Initialization
app = FastAPI(
    title="Sterling Catering API",
    redirect_slashes=False
)

# 3. CORS — reads from env, with safe localhost fallback for dev
raw_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Router Registration
# User & Member Routes
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(members.router, prefix="/api/members", tags=["members"])

# Reservation Routes
app.include_router(reservations.router, prefix="/api/reservations", tags=["reservations"])
app.include_router(reservation_attendees.router, prefix="/api/reservation-attendees", tags=["reservation-attendees"])
app.include_router(reservation_messages.router, prefix="/api/reservation-messages", tags=["messages"])

# Core Data Routes
app.include_router(dining_rooms.router, prefix="/api/dining-rooms", tags=["dining-rooms"])
app.include_router(menu_items.router, prefix="/api/menu-items", tags=["menu-items"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

# Orders Routes
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(order_items.router, prefix="/api/order-items", tags=["order-items"])

# Admin Configuration Routes
app.include_router(admin_dining_rooms.router, prefix="/api/admin/dining-rooms", tags=["admin-dining-rooms"])
app.include_router(admin_tables.router, prefix="/api/admin/tables", tags=["admin-tables"])
app.include_router(admin_seats.router, prefix="/api/admin/seats", tags=["admin-seats"])
app.include_router(admin_menu_items.router, prefix="/api/admin/menu-items", tags=["admin-menu-items"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["admin"])

# Operations / Staff Routes
app.include_router(ops.router, prefix="/api/ops", tags=["ops"])

# 5. Global Handlers & Root
@app.get("/")
def root():
    return {"message": "Sterling Catering API Operational"}

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    details = f"{type(exc).__name__}: {exc}"
    print(f"🔥 500 Error on {request.method} {request.url}: {details}")
    return error_server(details)