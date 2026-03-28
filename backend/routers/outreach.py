"""
Outreach router — send cold outreach emails via Resend.

Proxies Resend API calls through Railway (which has a clean IP)
so Ben D can send outreach autonomously without Cloudflare blocks.
"""
import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM = os.environ.get("RESEND_FROM_EMAIL", "ben.d@rivaledge.ai")
OUTREACH_FROM = "Ben D <ben.d@rivaledge.ai>"

# Allowlist of authorized senders (ben.d@rivaledge.ai only)
AUTHORIZED_SENDERS = {"ben.d@rivaledge.ai"}


class OutreachRequest(BaseModel):
    to: str  # recipient email
    subject: str
    body: str  # plain text body
    from_name: str = "Ben D"


class OutreachResponse(BaseModel):
    sent: bool
    email_id: Optional[str] = None
    message: str


@router.post("/send", response_model=OutreachResponse)
async def send_outreach_email(
    body: OutreachRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a cold outreach email via Resend.
    Auth required — only authorized accounts can send outreach.
    """
    user_email = current_user.get("email", "")
    if user_email not in AUTHORIZED_SENDERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send outreach emails.",
        )

    if not RESEND_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service not configured.",
        )

    # Basic validation
    if not body.to or "@" not in body.to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recipient email address.",
        )

    payload = {
        "from": f"{body.from_name} <{RESEND_FROM}>",
        "to": [body.to],
        "subject": body.subject,
        "text": body.body,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
            )

        if response.status_code == 200:
            data = response.json()
            logger.info("Outreach email sent to %s | id: %s", body.to, data.get("id"))
            return OutreachResponse(
                sent=True,
                email_id=data.get("id"),
                message=f"Email sent to {body.to}",
            )
        else:
            logger.error("Resend error %s: %s", response.status_code, response.text[:200])
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Email service error: {response.text[:100]}",
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Email service timed out.",
        )
    except Exception as exc:
        logger.error("Outreach send error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email.",
        )
