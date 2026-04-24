"""
Admin user upgrade endpoint
"""
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user
import db.supabase as db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin"])

# Admin user IDs (Clerk user IDs)
ADMIN_USER_IDS = [
    "user_3Bh6we4LE9YddryP143qpQsIcoX",  # Waters Deng
]


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin access."""
    user_id = current_user.get("sub", "")
    if user_id not in ADMIN_USER_IDS:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


class UpgradeResponse(BaseModel):
    success: bool
    user_email: str
    plan: str
    message: str


@router.post("/admin/upgrade-user", response_model=UpgradeResponse)
def admin_upgrade_user(
    user_email: str = Query(..., description="Email of user to upgrade"),
    plan: str = Query("pro", enum=["solo", "pro"]),
    admin_user: dict = Depends(require_admin),
):
    """
    Admin endpoint to manually upgrade any user to Pro or Solo.
    """
    try:
        # Find user by email using raw HTTP
        url = db._url(f"users?email=eq.{user_email}&limit=1")
        r = httpx.get(url, headers=db._headers(), timeout=10)
        users = r.json()
        
        if not isinstance(users, list) or len(users) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"User with email {user_email} not found"
            )
        
        user_id = users[0].get("id")
        
        # Update user plan using raw HTTP
        update_url = db._url(f"users?id=eq.{user_id}")
        headers = {**db._headers(), "Prefer": "return=representation"}
        update_r = httpx.patch(update_url, json={"plan": plan}, headers=headers, timeout=10)
        updated = update_r.json()
        
        if isinstance(updated, list) and len(updated) > 0:
            return {
                "success": True,
                "user_email": user_email,
                "plan": plan,
                "message": f"User upgraded to {plan} successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to update user plan"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upgrade user: {str(e)}"
        )
