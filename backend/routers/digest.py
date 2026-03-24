"""
Digest router — generate and send AI-powered competitor digests.

Day 3 feature.
"""
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_current_user
import db.supabase as db
import services.ai as ai_service
import services.email as email_service
from services.differ import diff_snapshots

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Helper ─────────────────────────────────────────────────────────────────────

def _extract_subject(html_content: str) -> str:
    """Pull subject from <!-- SUBJECT: ... --> comment, or use default."""
    match = re.search(r'<!--\s*SUBJECT:\s*(.+?)\s*-->', html_content)
    if match:
        return match.group(1).strip()
    return "Your RivalEdge Weekly Brief"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/generate")
def generate_digest_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Generate a weekly digest for the authenticated user.
    
    - Fetches all competitors
    - Gets latest + prior snapshots for each
    - Runs diff engine
    - Calls Claude to generate HTML digest
    - Saves to digests table
    - Returns digest_id + preview
    """
    user_id = current_user["sub"]
    
    # 1. Get all competitors
    competitors = db.get_competitors(user_id)
    
    if not competitors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No competitors to generate digest for. Add competitors first.",
        )
    
    # 2. Build competitors_with_diffs list
    competitors_with_diffs = []
    for comp in competitors:
        comp_id = comp["id"]
        latest = db.get_latest_snapshot(comp_id)
        prior = db.get_prior_snapshot(comp_id)
        
        if latest and prior:
            diff_result = diff_snapshots(prior["content"], latest["content"])
        elif latest:
            # First snapshot — no diff yet
            diff_result = {
                "has_changes": False,
                "changes": [],
                "significance_summary": "none",
            }
        else:
            # No snapshots at all
            diff_result = {
                "has_changes": False,
                "changes": [],
                "significance_summary": "none",
            }
        
        current_profile = comp.get("profile") or ""
        if isinstance(current_profile, dict):
            current_profile = str(current_profile)
        
        competitors_with_diffs.append({
            "competitor_name": comp.get("name") or comp.get("url"),
            "url": comp.get("url"),
            "diff_result": diff_result,
            "current_profile": current_profile,
        })
    
    # 3. Generate digest via Claude
    user_email = current_user.get("email", user_id)
    html_content = ai_service.generate_weekly_digest(user_email, competitors_with_diffs)
    
    # 4. Save to Supabase
    digest_record = db.create_digest(user_id=user_id, content=html_content)
    
    # 5. Return preview
    preview = html_content[:500]
    
    return {
        "digest_id": digest_record["id"],
        "preview": preview,
    }


@router.post("/send/{digest_id}")
def send_digest_endpoint(
    digest_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a previously-generated digest via Resend email.
    
    - Fetches digest from Supabase (user-scoped)
    - Sends via Resend
    - Updates sent_at timestamp
    """
    user_id = current_user["sub"]
    
    # 1. Fetch digest (scoped to user)
    digest = db.get_digest(digest_id, user_id)
    if not digest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digest not found",
        )
    
    # 2. Get user email from token
    user_email = current_user.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email not available in token",
        )
    
    # 3. Extract subject from HTML
    html_content = digest["content"]
    subject = _extract_subject(html_content)
    
    # 4. Send via Resend
    sent = email_service.send_digest(
        to_email=user_email,
        html_content=html_content,
        subject=subject,
    )
    
    if sent:
        # 5. Mark as sent
        db.mark_digest_sent(digest_id)
        return {"sent": True, "message": f"Digest sent to {user_email}"}
    else:
        return {"sent": False, "message": "Failed to send digest. Check logs for details."}


@router.post("/send-welcome")
def send_welcome_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Send a welcome email to the current user.
    Used when the first competitor is added.
    """
    user_id = current_user["sub"]
    user_email = current_user.get("email")
    
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email not available in token",
        )
    
    # Get first competitor name for personalization
    competitors = db.get_competitors(user_id)
    first_competitor = "your first competitor"
    if competitors:
        first_competitor = competitors[-1].get("name") or competitors[-1].get("url", "your competitor")
    
    sent = email_service.send_welcome_email(
        to_email=user_email,
        first_competitor=first_competitor,
    )
    
    return {"sent": sent}
