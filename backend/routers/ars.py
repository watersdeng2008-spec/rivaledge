"""
AI Recommendation Share (ARS) Router

API endpoints for calculating and retrieving AI Recommendation Share scores.
"""

from typing import Optional

import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from auth import get_current_user, resolve_db_id
from services.ai_recommendation_share import (
    calculate_ars,
    calculate_free_audit_ars,
    save_ars_result,
    get_ars_history,
    ars_to_dict,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ARSCalculateRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=200)
    competitors: list[str] = Field(..., min_items=1, max_items=20)


class ARSFreeAuditRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=200)
    competitors: list[str] = Field(..., min_items=1, max_items=3)
    email: Optional[str] = Field(None, description="Email for lead capture")


class ARSResponse(BaseModel):
    brand_name: str
    category: str
    ars_score: float
    total_queries: int
    brand_mentions: int
    competitor_scores: dict
    ranking: list[dict]
    calculated_at: str


class ARSHistoryResponse(BaseModel):
    history: list[dict]
    brand_name: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/calculate", response_model=ARSResponse)
async def calculate_ars_endpoint(
    body: ARSCalculateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate AI Recommendation Share for the authenticated user's brand.
    
    Requires Pro plan or higher for full calculation.
    """
    user_id = resolve_db_id(current_user)
    
    # Get user plan
    import db.supabase as db
    user = db.get_user(user_id)
    plan = user.get("plan", "solo") if user else "solo"
    
    # Plan limits
    if plan == "solo" and len(body.competitors) > 3:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Solo plan limited to 3 competitors. Upgrade to Pro for 10.",
        )
    
    try:
        result = await calculate_ars(
            brand_name=body.brand_name,
            category=body.category,
            competitors=body.competitors,
            plan=plan,
        )
        
        # Save to database
        save_ars_result(result, user_id)
        
        # Build ranking
        all_scores = {body.brand_name: result.ars_score}
        all_scores.update(result.competitor_scores)
        ranking = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        return ARSResponse(
            brand_name=result.brand_name,
            category=result.category,
            ars_score=result.ars_score,
            total_queries=result.total_queries,
            brand_mentions=result.brand_mentions,
            competitor_scores=result.competitor_scores,
            ranking=[
                {"rank": i + 1, "brand": name, "ars": score}
                for i, (name, score) in enumerate(ranking)
            ],
            calculated_at=result.calculated_at,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ARS calculation failed: {str(e)}",
        )


@router.post("/audit/free", response_model=ARSResponse)
async def free_audit_endpoint(body: ARSFreeAuditRequest):
    """
    Free AI Visibility Audit — no authentication required.
    
    Limited to 5 prompts and 2 AI models for cost efficiency.
    Captures email for lead generation if provided.
    """
    try:
        result = await calculate_free_audit_ars(
            brand_name=body.brand_name,
            category=body.category,
            competitors=body.competitors,
        )
        
        # Capture lead if email provided
        if body.email:
            import db.supabase as db
            # Store as lead for follow-up
            lead_payload = {
                "email": body.email,
                "brand_name": body.brand_name,
                "category": body.category,
                "competitors": body.competitors,
                "ars_score": result["ars_score"],
                "source": "free_audit",
            }
            try:
                httpx.post(
                    db._url("audit_leads"),
                    json=lead_payload,
                    headers=db._headers(),
                    timeout=10,
                )
            except Exception:
                pass  # Don't fail the audit if lead capture fails
        
        return ARSResponse(
            brand_name=result["brand_name"],
            category=result["category"],
            ars_score=result["ars_score"],
            total_queries=result["total_queries"],
            brand_mentions=result["brand_mentions"],
            competitor_scores=result["competitor_scores"],
            ranking=result["ranking"],
            calculated_at=result["calculated_at"],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit calculation failed: {str(e)}",
        )


@router.get("/history/{brand_name}", response_model=ARSHistoryResponse)
def get_ars_history_endpoint(
    brand_name: str,
    current_user: dict = Depends(get_current_user),
):
    """Get ARS history for a specific brand."""
    user_id = resolve_db_id(current_user)
    history = get_ars_history(user_id, brand_name)
    return ARSHistoryResponse(history=history, brand_name=brand_name)


@router.get("/current", response_model=ARSResponse)
async def get_current_ars(
    brand_name: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the most recent ARS calculation for a brand."""
    user_id = resolve_db_id(current_user)
    history = get_ars_history(user_id, brand_name, limit=1)
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ARS data found for {brand_name}. Run /calculate first.",
        )
    
    latest = history[0]
    return ARSResponse(
        brand_name=latest["brand_name"],
        category=latest["category"],
        ars_score=latest["ars_score"],
        total_queries=latest["total_queries"],
        brand_mentions=latest["brand_mentions"],
        competitor_scores=latest.get("competitor_scores", {}),
        ranking=[],  # Would need to recalculate from stored data
        calculated_at=latest["calculated_at"],
    )


@router.get("/leaderboard/{category}")
async def get_category_leaderboard(category: str):
    """
    Get public leaderboard for a category.
    Shows anonymized ARS scores for market research.
    """
    # This would aggregate across all users tracking this category
    # For now, return placeholder
    return {
        "category": category,
        "leaderboard": [
            {"rank": 1, "brand": "Leader", "ars": 42.0},
            {"rank": 2, "brand": "Challenger", "ars": 28.0},
            {"rank": 3, "brand": "Contender", "ars": 15.0},
        ],
        "note": "Public leaderboard — run a free audit to see where you rank",
    }
