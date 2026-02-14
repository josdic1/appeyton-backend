# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    users,
    members,
    reservations,
    reservation_attendees,
    dining_rooms,
    admin_dining_rooms,
    admin_tables,
    admin_users,
    ops,
)

app = FastAPI(
    title="Sterling Catering API",
    redirect_slashes=True  # ← Handles trailing slash automatically
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public routes
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Member routes (authenticated)
app.include_router(members.router, prefix="/api/members", tags=["members"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["reservations"])
app.include_router(reservation_attendees.router, prefix="/api/reservation-attendees", tags=["reservation-attendees"])

# Read-only routes for all authenticated users
app.include_router(dining_rooms.router, prefix="/api/dining-rooms", tags=["dining-rooms"])

# Admin-only routes
app.include_router(admin_dining_rooms.router, prefix="/api/admin/dining-rooms", tags=["admin-dining-rooms"])
app.include_router(admin_tables.router, prefix="/api/admin/tables", tags=["admin-tables"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["admin"])

# Ops routes (staff/admin)
app.include_router(ops.router, prefix="/api/ops", tags=["ops"])


@app.get("/")
def root():
    return {"message": "Sterling Catering API"}


@app.get("/health")
def health():
    return {"status": "ok"}