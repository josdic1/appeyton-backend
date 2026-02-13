# app/routes/admin_users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.permissions import require_min_role

router = APIRouter()

ALLOWED_ROLES = {"member", "staff", "admin"}


@router.patch("/users/{user_id}/role")
def set_user_role(
    user_id: int,
    role: str = Query(..., description="member | staff | admin"),
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_min_role("admin")),
):
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = user.role

    # prevent removing the last admin
    if old_role == "admin" and role != "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote the last admin")

    user.role = role
    db.commit()

    return {"ok": True, "user_id": user_id, "old_role": old_role, "new_role": role}
