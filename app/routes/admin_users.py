# app/routes/admin_users.py
from fastapi import APIRouter, Depends, HTTPException, Body, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.utils.permissions import load_acl, save_acl, get_current_user, get_permission
from datetime import datetime, timezone

router = APIRouter()

# ── NEW: Schema for Admin Creation (includes role/status) ──
class UserCreateAdmin(UserCreate):
    role: str = "member"
    membership_status: str = "active"
    guest_allowance: int = 4

# ── User management ───────────────────────────────────────────────────

# ── NEW: Create User Endpoint (Fixes 405 Error) ──
@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user_in: UserCreateAdmin,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "write")),
):
    """Admin create user with specific role and status."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_in.email,
        name=user_in.name,
        phone=user_in.phone,
        role=user_in.role,
        membership_status=user_in.membership_status,
        guest_allowance=user_in.guest_allowance,
        created_by_user_id=user.id
    )
    new_user.set_password(user_in.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    """Admin view of all users."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    """Admin fetch of any user by ID."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return target


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "write")),
):
    """Admin update of any user's fields including role and status."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    for field, val in user_in.model_dump(exclude_unset=True).items():
        if field == "password":
            if val:
                target.set_password(val)
        else:
            setattr(target, field, val)
    target.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(target)
    return target


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "delete")),
):
    """Admin delete of a user. Cannot delete yourself."""
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target)
    db.commit()


# ── Role management ───────────────────────────────────────────────────
@router.patch("/users/{user_id}/role")
def set_user_role(
    user_id: int,
    role: str = Query(..., description="member | staff | admin"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Only admins can modify roles")
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.role == "admin" and role != "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote last admin")
    target_user.role = role
    db.commit()
    return {"ok": True, "new_role": role}


# ── Permissions matrix ────────────────────────────────────────────────
@router.get("/permissions/matrix")
def get_live_matrix(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    if user.role != "admin" or scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    return load_acl(db)


@router.get("/activity-logs")
def get_activity_logs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(50).all()


@router.get("/permissions/history")
def get_permissions_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.action == "update_permissions")
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/permissions/matrix")
def update_matrix(
    request: Request,
    new_acl: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "write")),
):
    if user.role != "admin" or scope != "all":
        raise HTTPException(status_code=403, detail="Unauthorized")
    save_acl(
        db=db,
        user_id=user.id,
        new_acl=new_acl,
        ip=request.client.host if request.client else "unknown",
    )
    return {"status": "success", "message": "ACL updated and logged"}