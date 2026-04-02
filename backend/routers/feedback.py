"""
Feedback router — collect user feedback.
"""
import logging
from typing import Optional
import httpx
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


class FeedbackRequest(BaseModel):
    reaction: str
    message: Optional[str] = None
    page: Optional[str] = None


@router.post("")
async def submit_feedback(
    body: FeedbackRequest,
    current_user: dict = Depends(get_current_user),
):
    """Save user feedback to Supabase."""
    user_id = current_user.get("sub", "anonymous")
    
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if supabase_url and supabase_key:
        try:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "user_id": user_id,
                "reaction": body.reaction,
                "message": body.message,
                "page": body.page,
            }
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"{supabase_url}/rest/v1/feedback",
                    json=payload,
                    headers=headers,
                )
            logger.info("Feedback saved: user=%s reaction=%s", user_id[:15], body.reaction)
        except Exception as e:
            logger.error("Failed to save feedback: %s", e)
    
    return {"saved": True}
