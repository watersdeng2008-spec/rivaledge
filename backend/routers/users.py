"""
Users router — profile and account endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user, resolve_db_id
import db.supabase as db

router = APIRouter()


class UserProfile(BaseModel):
    id: str
    email: str
    plan: str


@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    user_id = resolve_db_id(current_user)
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
    user_id = resolve_db_id(current_user)
    email = current_user.get("email", "")
    if not email:
        # Clerk may put email in different claim depending on template
        email = current_user.get("email_addresses", [{}])[0].get("email_address", "")

    existing = db.get_user(user_id)
    if existing:
        # User already exists — only update email, don't touch plan
        user = db.upsert_user(user_id=user_id, email=email)
    else:
        # New user — create record; upsert_user handles email dedup + plan preservation
        user = db.upsert_user(user_id=user_id, email=email)
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
    user_id = resolve_db_id(current_user)

    result = db.update_user_profile(user_id, {
        "company_name": body.company_name,
        "business_description": body.business_description,
        "industry": body.industry,
        "onboarding_completed": True,
    })

    if not result:
        raise HTTPException(status_code=500, detail="Failed to save onboarding data")

    return {"saved": True, "company_name": body.company_name}


@router.get("/me/debug")
def debug_auth_chain(current_user: dict = Depends(get_current_user)):
    """Debug endpoint: trace the full auth→DB→billing chain.
    Shows exactly which JWT sub, which DB record, and which plan."""
    user_id = resolve_db_id(current_user)
    email = current_user.get("email", "")
    if not email:
        email_addresses = current_user.get("email_addresses", [])
        email = email_addresses[0].get("email_address", "") if email_addresses else ""

    # What DB returns for this JWT sub
    db_user_by_id = db.get_user(user_id)

    # What DB returns for this email
    db_user_by_email = db.get_user_by_email(email) if email else None

    return {
        "jwt_sub": user_id,
        "jwt_email": email,
        "db_by_id": {
            "found": db_user_by_id is not None,
            "id": db_user_by_id["id"] if db_user_by_id else None,
            "plan": db_user_by_id.get("plan") if db_user_by_id else None,
            "email": db_user_by_id.get("email") if db_user_by_id else None,
        },
        "db_by_email": {
            "found": db_user_by_email is not None,
            "id": db_user_by_email["id"] if db_user_by_email else None,
            "plan": db_user_by_email.get("plan") if db_user_by_email else None,
        },
        "plan_match": (db_user_by_id.get("plan") if db_user_by_id else None) == (db_user_by_email.get("plan") if db_user_by_email else None),
        "id_match": (db_user_by_id["id"] if db_user_by_id else None) == (db_user_by_email["id"] if db_user_by_email else None),
    }
