"""
Email API routes for sending competitive intelligence reports and notifications.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from services.email_service import send_competitive_intelligence_report, send_welcome_email
from auth import get_current_user

router = APIRouter(tags=["email"])

class SendReportRequest(BaseModel):
    to_email: str
    to_name: str
    company_name: str
    report_content: str
    subject: Optional[str] = None

class SendWelcomeRequest(BaseModel):
    to_email: str
    to_name: str
    company_name: str

@router.post("/api/email/send-report")
async def send_report(
    request: SendReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a competitive intelligence report email.
    Requires authentication.
    """
    result = send_competitive_intelligence_report(
        to_email=request.to_email,
        to_name=request.to_name,
        company_name=request.company_name,
        report_content=request.report_content,
        subject=request.subject
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "message_id": result.get("message_id"),
        "to": result["to"]
    }

@router.post("/api/email/send-welcome")
async def send_welcome(
    request: SendWelcomeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send welcome email to new user.
    """
    result = send_welcome_email(
        to_email=request.to_email,
        to_name=request.to_name,
        company_name=request.company_name
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "message_id": result.get("message_id"),
        "to": result["to"]
    }
