"""
Test email endpoint - no auth required for testing only.
Remove or protect before production scale.
"""
from fastapi import APIRouter, Query
from services.email_service import send_welcome_email

router = APIRouter(tags=["Test"])

@router.post("/send-welcome")
async def test_send_welcome(
    to_email: str = Query(..., description="Recipient email"),
    to_name: str = Query(default="Test User", description="Recipient name"),
    company_name: str = Query(default="Test Company", description="Company name"),
):
    """
    Test endpoint to send a welcome email without authentication.
    """
    result = send_welcome_email(
        to_email=to_email,
        to_name=to_name,
        company_name=company_name
    )
    
    return result
