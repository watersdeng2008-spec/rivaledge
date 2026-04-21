from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db.supabase import get_user, upsert_user
from auth import get_current_user

router = APIRouter(tags=["onboarding"])

class OnboardingStep1(BaseModel):
    company_name: str
    company_url: Optional[str] = None
    industry: Optional[str] = None

class OnboardingStep2(BaseModel):
    tracking_preferences: List[str]

@router.post("/step/1")
async def save_step_1(data: OnboardingStep1, current_user: dict = Depends(get_current_user)):
    user_id = current_user["sub"]  # Clerk uses "sub" not "id"
    result = upsert_user(user_id, {
        "company_name": data.company_name,
        "company_url": data.company_url,
        "industry": data.industry,
        "onboarding_step": 1,
        "onboarding_started_at": "now()"
    })
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save")
    return {"success": True, "next_step": 2}

@router.post("/step/2")
async def save_step_2(data: OnboardingStep2, current_user: dict = Depends(get_current_user)):
    user_id = current_user["sub"]  # Clerk uses "sub" not "id"
    result = upsert_user(user_id, {
        "tracking_preferences": data.tracking_preferences,
        "onboarding_step": 2
    })
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save")
    return {"success": True, "next_step": 3}

@router.get("/status")
async def get_onboarding_status(current_user: dict = Depends(get_current_user)):
    return {
        "step": current_user.get("onboarding_step", 0),
        "completed": current_user.get("onboarding_completed", False),
        "company_name": current_user.get("company_name"),
        "industry": current_user.get("industry"),
        "tracking_preferences": current_user.get("tracking_preferences", [])
    }
