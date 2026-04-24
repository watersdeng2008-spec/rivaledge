"""
Admin user upgrade endpoint
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user
from db.supabase import get_user_by_email, update_user_plan

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
        # Find user by email
        user = get_user_by_email(user_email)

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with email {user_email} not found"
            )

        # Update user plan
        update_user_plan(user.get("id"), plan)

        return {
            "success": True,
            "user_email": user_email,
            "plan": plan,
            "message": f"User upgraded to {plan} successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upgrade user: {str(e)}"
        )
