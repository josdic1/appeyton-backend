# app/routes/users.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
from app.utils.auth import create_access_token, get_current_user, BLOCKED_STATUSES

router = APIRouter()


# ── Public: no auth required ──────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not user.check_password(payload.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.membership_status in BLOCKED_STATUSES:
        raise HTTPException(
            status_code=403,
            detail=f"Account {user.membership_status}. Contact an administrator.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return {
        "access_token": create_access_token(user_id=user.id, role=user.role),
        "token_type": "bearer",
        "user": user,
    }


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        name=user_in.name,
        role="member",
        membership_status="active",
        guest_allowance=4,
    )
    user.set_password(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Authenticated: must be logged in ─────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Returns the currently logged in user's own profile."""
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Allows a user to update their own profile only."""
    for field, val in user_in.model_dump(exclude_unset=True).items():
        if field == "password":
            if val:
                user.set_password(val)
        elif field in ("role", "membership_status"):
            raise HTTPException(status_code=403, detail=f"Cannot self-modify {field}")
        else:
            setattr(user, field, val)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user