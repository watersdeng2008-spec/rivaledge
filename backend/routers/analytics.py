"""
Analytics router for PostHog event tracking
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from services.analytics import (
    track_event,
    identify_user,
    track_user_signup,
    track_user_login,
    track_report_generated,
    track_competitor_added,
    track_subscription_created,
    track_email_sent,
    track_sales_outreach_sent
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class TrackEventRequest(BaseModel):
    event_name: str
    properties: Optional[Dict[str, Any]] = None


class IdentifyUserRequest(BaseModel):
    user_id: str
    properties: Optional[Dict[str, Any]] = None


@router.post("/track")
async def track_event_endpoint(
    request: TrackEventRequest,
    req: Request
):
    """
    Track a custom event in PostHog
    
    Example:
    {
        "event_name": "button_clicked",
        "properties": {"button_id": "generate_report", "page": "dashboard"}
    }
    """
    # Get user ID from request state if authenticated
    user_id = getattr(req.state, "user_id", None)
    
    track_event(
        event_name=request.event_name,
        user_id=user_id,
        properties=request.properties
    )
    
    return {"status": "ok", "event_tracked": request.event_name}


@router.post("/identify")
async def identify_user_endpoint(request: IdentifyUserRequest):
    """
    Identify a user with traits in PostHog
    
    Example:
    {
        "user_id": "user_123",
        "properties": {"email": "user@example.com", "plan": "pro"}
    }
    """
    identify_user(
        user_id=request.user_id,
        properties=request.properties
    )
    
    return {"status": "ok", "user_identified": request.user_id}


@router.post("/track/signup")
async def track_signup(
    user_id: str,
    email: str,
    signup_source: str = "organic"
):
    """Track user signup event"""
    track_user_signup(user_id=user_id, email=email, signup_source=signup_source)
    return {"status": "ok"}


@router.post("/track/login")
async def track_login(
    user_id: str,
    method: str = "email"
):
    """Track user login event"""
    track_user_login(user_id=user_id, method=method)
    return {"status": "ok"}


@router.post("/track/report-generated")
async def track_report(
    user_id: str,
    report_type: str,
    competitor_count: int = 0,
    generation_time_ms: Optional[int] = None
):
    """Track report generation event"""
    track_report_generated(
        user_id=user_id,
        report_type=report_type,
        competitor_count=competitor_count,
        generation_time_ms=generation_time_ms
    )
    return {"status": "ok"}


@router.post("/track/competitor-added")
async def track_competitor(
    user_id: str,
    competitor_name: str,
    competitor_domain: str
):
    """Track competitor addition event"""
    track_competitor_added(
        user_id=user_id,
        competitor_name=competitor_name,
        competitor_domain=competitor_domain
    )
    return {"status": "ok"}


@router.post("/track/subscription")
async def track_subscription(
    user_id: str,
    plan: str,
    amount: float,
    currency: str = "USD"
):
    """Track subscription creation event"""
    track_subscription_created(
        user_id=user_id,
        plan=plan,
        amount=amount,
        currency=currency
    )
    return {"status": "ok"}


@router.post("/track/email-sent")
async def track_email(
    user_id: str,
    email_type: str,
    recipient_count: int = 1
):
    """Track email sent event"""
    track_email_sent(
        user_id=user_id,
        email_type=email_type,
        recipient_count=recipient_count
    )
    return {"status": "ok"}


@router.post("/track/sales-outreach")
async def track_outreach(
    leads_count: int,
    campaign_id: str,
    success_rate: float
):
    """Track sales outreach automation event"""
    track_sales_outreach_sent(
        leads_count=leads_count,
        campaign_id=campaign_id,
        success_rate=success_rate
    )
    return {"status": "ok"}


@router.get("/config")
async def get_analytics_config():
    """Get PostHog configuration for frontend"""
    import os
    
    return {
        "posthog_api_key": os.getenv("POSTHOG_API_KEY", ""),
        "posthog_host": os.getenv("POSTHOG_HOST", "https://app.posthog.com"),
        "debug": os.getenv("POSTHOG_DEBUG", "false").lower() == "true"
    }
