# app/routes/users.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.utils.auth import create_access_token, get_current_user

router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user_in.email,
        name=user_in.name,
        phone=user_in.phone,
        role="member",
        membership_status="active",
        guest_allowance=4,
        meta=None,
        created_by_user_id=None,  # set this if an admin creates users
    )
    new_user.set_password(user_in.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login/", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.check_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # update last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
