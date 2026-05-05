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

    existing = db.get_user(user_id)
    if existing:
        # User already exists — only update email, don't touch plan
        user = db.upsert_user(user_id=user_id, email=email)
    else:
        # New user — create with solo plan
        user = db.upsert_user(user_id=user_id, email=email, plan="solo")
    return UserProfile(**user)


class OnboardingData(BaseModel):
    company_name: str
    business_description: str = ""
    industry: str = ""


@router.post("/onboarding")
def save_onboarding(
    body: OnboardingData,
    current_user: dict = Depends(get_current_user),
):
    """Save onboarding info — company name, description, industry."""
    user_id = current_user["sub"]

    result = db.update_user_profile(user_id, {
        "company_name": body.company_name,
        "business_description": body.business_description,
        "industry": body.industry,
        "onboarding_completed": True,
    })

    if not result:
        raise HTTPException(status_code=500, detail="Failed to save onboarding data")

    return {"saved": True, "company_name": body.company_name}
