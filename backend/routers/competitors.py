"""
Competitors router — CRUD for tracked competitor URLs.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl

from auth import get_current_user
import db.supabase as db

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────────

class CompetitorCreate(BaseModel):
    url: HttpUrl
    name: Optional[str] = None


class CompetitorResponse(BaseModel):
    id: str
    user_id: str
    url: str
    name: Optional[str]
    profile: Optional[dict]
    created_at: str


class CompetitorList(BaseModel):
    competitors: list[CompetitorResponse]
    total: int


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/", response_model=CompetitorList)
def list_competitors(current_user: dict = Depends(get_current_user)):
    """List all competitors tracked by the authenticated user."""
    user_id = current_user["sub"]
    competitors = db.get_competitors(user_id)
    return CompetitorList(
        competitors=[CompetitorResponse(**c) for c in competitors],
        total=len(competitors),
    )


@router.post("/", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def add_competitor(
    body: CompetitorCreate,
    current_user: dict = Depends(get_current_user),
):
    """Add a new competitor URL to track."""
    user_id = current_user["sub"]
    
    # Plan limits: solo = 5 competitors
    existing = db.get_competitors(user_id)
    user = db.get_user(user_id)
    plan = user.get("plan", "solo") if user else "solo"
    
    limits = {"solo": 3, "pro": 10}
    limit = limits.get(plan, 3)
    
    if len(existing) >= limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Plan limit reached ({limit} competitors). Upgrade to add more.",
        )
    
    competitor = db.create_competitor(
        user_id=user_id,
        url=str(body.url),
        name=body.name,
    )
    return CompetitorResponse(**competitor)


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_competitor(
    competitor_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """Remove a competitor from tracking."""
    user_id = current_user["sub"]
    db.delete_competitor(str(competitor_id), user_id)
