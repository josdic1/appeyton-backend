from fastapi import APIRouter, Depends, HTTPException, Body, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.utils.permissions import load_acl, save_acl, get_current_user, get_permission

router = APIRouter()

@router.get("/permissions/matrix")
def get_live_matrix(
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read"))
):
    if user.role != "admin" or scope != "all":
        raise HTTPException(status_code=403, detail="Admin access required")
    return load_acl()


@router.get("/activity-logs")
def get_activity_logs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")) #
):
    """
    Fetches the latest 50 security actions for the dashboard history log.
    Requires Admin access ('all' scope).
    """
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
        
    # Query the ActivityLog model and sort by newest first
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(50).all()

@router.get("/permissions/history")
def get_permissions_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read"))
):
    """Fetches high-level activity logs specifically for permission changes."""
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
    scope: str = Depends(get_permission("User", "write")) 
):
    """Saves new permissions and populates the ActivityLog via the utility."""
    if user.role != "admin" or scope != "all":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Passing 'db' and 'user.id' to trigger the ActivityLog record
    save_acl(
        db=db, 
        user_id=user.id, 
        new_acl=new_acl, 
        ip=request.client.host if request.client else "unknown"
    )
    return {"status": "success", "message": "ACL updated and logged"}

@router.patch("/users/{user_id}/role")
def set_user_role(
    user_id: int,
    role: str = Query(..., description="member | staff | admin"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "write")),
):
    """Modifies user roles with safety checks for the last admin."""
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