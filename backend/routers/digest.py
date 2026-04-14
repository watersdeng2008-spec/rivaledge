"""
Digest router — generate and send AI-powered competitor digests.

Day 3 feature.
"""
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth import get_current_user
from rate_limit import limiter
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
@limiter.limit("5/hour")
def generate_digest_endpoint(request: Request, current_user: dict = Depends(get_current_user)):
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
    
    # 3. Generate digest via AI
    user_email = current_user.get("email", user_id)
    
    # Check if we have any usable data
    has_any_data = any(
        comp.get("current_profile") or comp.get("diff_result", {}).get("has_changes")
        for comp in competitors_with_diffs
    )
    
    if not has_any_data:
        # No data yet — return a helpful message
        logger.warning(f"User {user_id} has competitors but no scraped data yet")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your competitors are being analyzed. Please try again in a few minutes, or check back tomorrow for your first weekly digest.",
        )
    
    try:
        html_content = ai_service.generate_weekly_digest(user_email, competitors_with_diffs)
    except Exception as e:
        logger.error(f"Failed to generate digest: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}",
        )
    
    # 4. Save to Supabase
    digest_record = db.create_digest(user_id=user_id, content=html_content)
    
    # 5. Return preview
    preview = html_content
    
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


@router.post("/battle-card")
def battle_card_endpoint(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a battle card for a specific competitor.

    Body: {"competitor_id": str}
    Returns: {"battle_card": str (markdown)}
    """
    user_id = current_user["sub"]
    competitor_id = body.get("competitor_id")

    if not competitor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="competitor_id is required",
        )

    # Verify competitor belongs to user
    competitors = db.get_competitors(user_id)
    competitor = next((c for c in competitors if c["id"] == competitor_id), None)
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )

    # Build competitor profile string
    profile = competitor.get("profile") or {}
    if isinstance(profile, dict):
        profile_str = str(profile)
    else:
        profile_str = str(profile)

    competitor_data = {
        "name": competitor.get("name") or competitor.get("url"),
        "url": competitor.get("url"),
        "profile": profile_str,
    }

    our_product = {
        "name": "RivalEdge",
        "pricing": "$49/mo Solo, $99/mo Pro",
        "features": ["AI weekly digests", "Competitor monitoring", "Battle cards", "Pricing alerts"]
    }
    battle_card = ai_service.generate_battle_card(
        competitor_name=competitor_data["name"],
        competitor_profile={"url": competitor_data["url"], "profile": competitor_data["profile"]},
        our_product=our_product,
    )
    return {"battle_card": battle_card}


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


# ── Cold Outreach Email (added to digest router for reliability) ────────────

import httpx as _httpx
import os as _os
from pydantic import BaseModel as _BaseModel


# Alias to use locally
BaseModel = _BaseModel

AUTHORIZED_OUTREACH_SENDERS = {"ben.d@rivaledge.ai"}


class OutreachEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    from_name: str = "Ben D"


class OutreachEmailResponse(BaseModel):
    sent: bool
    email_id: Optional[str] = None
    message: str


@router.post("/outreach/send", response_model=OutreachEmailResponse)
async def send_outreach_email(
    body: OutreachEmailRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send cold outreach email via Resend (proxied through Railway IP)."""
    user_email = current_user.get("email", "")
    if user_email not in AUTHORIZED_OUTREACH_SENDERS:
        raise HTTPException(status_code=403, detail="Not authorized to send outreach emails.")

    resend_key = _os.environ.get("RESEND_API_KEY", "")
    resend_from = _os.environ.get("RESEND_FROM_EMAIL", "ben.d@rivaledge.ai")

    if not resend_key:
        raise HTTPException(status_code=503, detail="Email service not configured.")

    if not body.to or "@" not in body.to:
        raise HTTPException(status_code=400, detail="Invalid recipient email.")

    payload = {
        "from": f"{body.from_name} <{resend_from}>",
        "to": [body.to],
        "subject": body.subject,
        "text": body.body,
    }

    async with _httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            json=payload,
            headers={"Authorization": f"Bearer {resend_key}"},
        )

    if resp.status_code == 200:
        data = resp.json()
        logger.info("Outreach sent to %s | id: %s", body.to, data.get("id"))
        return OutreachEmailResponse(sent=True, email_id=data.get("id"), message=f"Sent to {body.to}")

    raise HTTPException(status_code=502, detail=f"Resend error: {resp.text[:100]}")
