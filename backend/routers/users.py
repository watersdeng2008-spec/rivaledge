"""
Users router — profile and account endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user
import db.supabase as db

router = APIRouter()


class UserProfile(BaseModel):
    id: str
    email: str
    plan: str


@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    user_id = current_user["sub"]
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please sign in to create an account.",
        )
    return UserProfile(**user)


@router.post("/me", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def create_or_update_me(current_user: dict = Depends(get_current_user)):
    """
    Upsert the authenticated user's record.
    Called after first sign-in to ensure user exists in DB.
    """
    user_id = current_user["sub"]
    email = current_user.get("email", "")
    if not email:
        # Clerk may put email in different claim depending on template
        email = current_user.get("email_addresses", [{}])[0].get("email_address", "")

    user = db.upsert_user(user_id=user_id, email=email)
    return UserProfile(**user)
