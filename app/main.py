# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    ops,
)
from app.utils.toast_responses import error_server, error_not_found as toast_not_found

app = FastAPI(
    title="Sterling Catering API",
    redirect_slashes=True
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
app.include_router(menu_items.router, prefix="/api/menu-items", tags=["menu-items"])

# Orders - Members order for self, Staff orders for anyone
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(order_items.router, prefix="/api/order-items", tags=["order-items"])

# Admin-only routes
app.include_router(admin_dining_rooms.router, prefix="/api/admin/dining-rooms", tags=["admin-dining-rooms"])
app.include_router(admin_tables.router, prefix="/api/admin/tables", tags=["admin-tables"])
app.include_router(admin_menu_items.router, prefix="/api/admin/menu-items", tags=["admin-menu-items"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["admin"])

# Ops routes (staff/admin)
app.include_router(ops.router, prefix="/api/ops", tags=["ops"])


@app.get("/")
def root():
    return {"message": "Sterling Catering API"}


@app.get("/health")
def health():
    return {"status": "ok"}


# Exception handlers (must be at the end)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 Not Found errors"""
    return JSONResponse(
        status_code=404,
        content=toast_not_found("Page").model_dump()
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handle 500 Internal Server errors"""
    return JSONResponse(
        status_code=500,
        content=error_server(str(exc)).model_dump()
    )