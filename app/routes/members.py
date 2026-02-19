# app/routes/members.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse
from app.utils.auth import get_current_user
from app.utils import toast_responses

router = APIRouter(tags=["members"])


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Adds a new family member or guest profile."""
    
    if payload.relation and payload.relation.lower() == "self":
        existing_self = db.query(Member).filter(
            Member.user_id == user.id,
            Member.relation.ilike("self")
        ).first()
        if existing_self:
            return toast_responses.error_validation(
                field="relation",
                issue="A 'self' profile already exists.",
                suggestion="Update your existing profile instead."
            )
    
    existing_name = db.query(Member).filter(
        Member.user_id == user.id,
        Member.name == payload.name
    ).first()
    if existing_name:
        return toast_responses.error_validation(
            field="name",
            issue=f"Member '{payload.name}' already exists.",
            suggestion="Use a nickname or unique identifier."
        )
    
    m = Member(
        user_id=user.id,
        created_by_user_id=user.id,
        name=payload.name,
        relation=payload.relation,
        dietary_restrictions=payload.dietary_restrictions,
        meta=payload.meta,
    )
    db.add(m)
    
    try:
        db.commit()
        db.refresh(m)
        return m
    except IntegrityError:
        db.rollback()
        return toast_responses.error_server("Database integrity conflict.")


@router.get("", response_model=List[MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Member).filter(Member.user_id == user.id).order_by(Member.id.asc()).all()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not m:
        return toast_responses.error_not_found("Member", member_id)
    return m


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not m:
        return toast_responses.error_not_found("Member", member_id)

    if payload.relation and payload.relation.lower() == "self":
        existing_self = db.query(Member).filter(
            Member.user_id == user.id,
            Member.relation.ilike("self"),
            Member.id != member_id
        ).first()
        if existing_self:
            return toast_responses.error_validation("relation", "Another profile is already 'self'.", "Change the relation.")
    
    if payload.name and payload.name != m.name:
        existing_name = db.query(Member).filter(
            Member.user_id == user.id,
            Member.name == payload.name,
            Member.id != member_id
        ).first()
        if existing_name:
            return toast_responses.error_validation("name", "Name conflict.", "Provide a unique name.")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(m, k, v)

    db.commit()
    db.refresh(m)
    return m


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not m:
        return toast_responses.error_not_found("Member", member_id)
        
    db.delete(m)
    db.commit()
    return None