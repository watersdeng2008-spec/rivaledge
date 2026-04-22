"""
Admin user upgrade endpoint
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user
from db.supabase import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

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


@router.post("/upgrade-user", response_model=UpgradeResponse)
def admin_upgrade_user(
    user_email: str = Query(..., description="Email of user to upgrade"),
    plan: str = Query("pro", enum=["solo", "pro"]),
    admin_user: dict = Depends(require_admin),
):
    """
    Admin endpoint to manually upgrade any user to Pro or Solo.
    """
    try:
        supabase = get_supabase_client()
        
        # Find user by email
        result = supabase.table("users").select("*").eq("email", user_email).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"User with email {user_email} not found"
            )
        
        # Update user plan
        update_result = supabase.table("users").update({"plan": plan}).eq("email", user_email).execute()
        
        if update_result.data:
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
