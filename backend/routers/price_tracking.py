"""
Price tracking router for RivalEdge
API endpoints for managing price tracking preferences and alerts
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from pydantic import BaseModel
import os

from auth import get_current_user
from rate_limit import limiter
import db.supabase as db

# Admin secret for cron jobs (set in Railway environment variables)
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "dev-secret-change-in-production")
from services.price_tracker import (
    process_price_alerts,
    process_and_send_pending_alerts,
    check_price_changes
)

router = APIRouter(prefix="/price-tracking", tags=["price_tracking"])


# ── Request/Response Models ───────────────────────────────────────────────────

class PriceTrackingSettings(BaseModel):
    track_pricing: bool
    alert_threshold: Optional[float] = 0.02  # 2% default


class CompetitorPriceSettings(BaseModel):
    track_pricing: bool
    retail_channels: Optional[List[str]] = None


class PriceAlertResponse(BaseModel):
    id: str
    competitor_id: str
    competitor_name: str
    old_price: float
    new_price: float
    change_percent: float
    direction: str
    channel: str
    status: str
    created_at: str


# ── User Settings Endpoints ───────────────────────────────────────────────────

@router.get("/settings")
@limiter.limit("30/minute")
def get_price_tracking_settings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current price tracking settings for the authenticated user.
    """
    user_id = current_user["sub"]
    user = db.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "track_pricing": user.get("track_pricing", False),
        "alert_threshold": user.get("price_alert_threshold", 0.02),
        "user_id": user_id
    }


@router.post("/settings")
@limiter.limit("10/minute")
def update_price_tracking_settings(
    request: Request,
    settings: PriceTrackingSettings,
    current_user: dict = Depends(get_current_user)
):
    """
    Update price tracking settings for the authenticated user.
    
    - track_pricing: Enable/disable price tracking
    - alert_threshold: Minimum price change percentage to trigger alert (e.g., 0.02 for 2%)
    """
    user_id = current_user["sub"]
    
    success = db.update_user_price_tracking(
        user_id=user_id,
        track_pricing=settings.track_pricing,
        alert_threshold=settings.alert_threshold
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )
    
    return {
        "status": "ok",
        "track_pricing": settings.track_pricing,
        "alert_threshold": settings.alert_threshold
    }


# ── Competitor Settings Endpoints ─────────────────────────────────────────────

@router.get("/competitors/{competitor_id}/settings")
@limiter.limit("30/minute")
def get_competitor_price_settings(
    request: Request,
    competitor_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get price tracking settings for a specific competitor.
    """
    user_id = current_user["sub"]
    
    # Verify competitor belongs to user
    competitors = db.get_competitors(user_id)
    competitor = next((c for c in competitors if c.get("id") == competitor_id), None)
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    return {
        "competitor_id": competitor_id,
        "track_pricing": competitor.get("track_pricing", False),
        "retail_channels": competitor.get("retail_channels", ["website"]),
        "competitor_name": competitor.get("name", "Unknown")
    }


@router.post("/competitors/{competitor_id}/settings")
@limiter.limit("10/minute")
def update_competitor_price_settings(
    request: Request,
    competitor_id: str,
    settings: CompetitorPriceSettings,
    current_user: dict = Depends(get_current_user)
):
    """
    Update price tracking settings for a specific competitor.
    
    - track_pricing: Enable/disable price tracking for this competitor
    - retail_channels: List of channels to monitor (e.g., ["amazon", "walmart", "website"])
    """
    user_id = current_user["sub"]
    
    # Verify competitor belongs to user
    competitors = db.get_competitors(user_id)
    competitor = next((c for c in competitors if c.get("id") == competitor_id), None)
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    success = db.update_competitor_price_tracking(
        competitor_id=competitor_id,
        track_pricing=settings.track_pricing,
        retail_channels=settings.retail_channels
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update competitor settings"
        )
    
    return {
        "status": "ok",
        "competitor_id": competitor_id,
        "track_pricing": settings.track_pricing,
        "retail_channels": settings.retail_channels
    }


# ── Alert Endpoints ───────────────────────────────────────────────────────────

@router.get("/alerts")
@limiter.limit("30/minute")
def get_price_alerts(
    request: Request,
    status: Optional[str] = "pending",
    current_user: dict = Depends(get_current_user)
):
    """
    Get price alerts for the authenticated user.
    
    Query params:
    - status: Filter by status (pending, sent, dismissed). Default: pending
    """
    user_id = current_user["sub"]
    
    if status == "pending":
        alerts = db.get_pending_price_alerts(user_id)
    else:
        # For other statuses, we'd need to add a more general query function
        alerts = []
    
    # Enrich with competitor names
    competitors = db.get_competitors(user_id)
    competitor_map = {c.get("id"): c.get("name", "Unknown") for c in competitors}
    
    enriched_alerts = []
    for alert in alerts:
        enriched_alerts.append({
            "id": alert.get("id"),
            "competitor_id": alert.get("competitor_id"),
            "competitor_name": competitor_map.get(alert.get("competitor_id"), "Unknown"),
            "old_price": alert.get("old_price"),
            "new_price": alert.get("new_price"),
            "change_percent": alert.get("change_percent"),
            "channel": alert.get("channel"),
            "status": alert.get("status"),
            "created_at": alert.get("created_at"),
            "sent_at": alert.get("sent_at")
        })
    
    return {
        "alerts": enriched_alerts,
        "count": len(enriched_alerts)
    }


@router.post("/alerts/{alert_id}/dismiss")
@limiter.limit("10/minute")
def dismiss_price_alert(
    request: Request,
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Dismiss a price alert.
    """
    user_id = current_user["sub"]
    
    # Verify alert belongs to user
    alerts = db.get_pending_price_alerts(user_id)
    alert = next((a for a in alerts if a.get("id") == alert_id), None)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update status to dismissed
    from datetime import datetime, timezone
    update_data = {
        "status": "dismissed",
        "dismissed_at": datetime.now(timezone.utc).isoformat()
    }
    
    # We'd need to add a function to update alerts, using generic approach for now
    success = True  # Placeholder
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss alert"
        )
    
    return {"status": "ok", "alert_id": alert_id}


# ── Admin/Scanning Endpoints ──────────────────────────────────────────────────

@router.post("/admin/scan")
@limiter.limit("5/hour")
def trigger_price_scan(
    request: Request,
    x_admin_secret: str = Header(None, alias="X-Admin-Secret")
):
    """
    Admin endpoint to manually trigger a price scan.
    Processes all users with price tracking enabled.
    Requires X-Admin-Secret header for authentication.
    """
    # Verify admin secret
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin secret"
        )
    
    result = process_price_alerts()
    
    return {
        "status": "ok",
        "scan_result": result
    }


@router.post("/admin/send-alerts")
@limiter.limit("5/hour")
def send_pending_alerts(
    request: Request,
    x_admin_secret: str = Header(None, alias="X-Admin-Secret")
):
    """
    Admin endpoint to send all pending price alert emails.
    Requires X-Admin-Secret header for authentication.
    """
    # Verify admin secret
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin secret"
        )
    
    result = process_and_send_pending_alerts()
    
    return {
        "status": "ok",
        "send_result": result
    }


@router.get("/admin/stats")
@limiter.limit("30/minute")
def get_price_tracking_stats(
    request: Request,
    x_admin_secret: str = Header(None, alias="X-Admin-Secret")
):
    """
    Get price tracking statistics (admin only).
    Requires X-Admin-Secret header for authentication.
    """
    # Verify admin secret
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin secret"
        )
    
    # Get counts
    users_with_tracking = db.get_users_with_price_tracking()
    pending_alerts = db.get_pending_price_alerts()
    
    return {
        "users_with_price_tracking": len(users_with_tracking),
        "pending_alerts": len(pending_alerts),
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
    }


# ── Manual Check Endpoint ─────────────────────────────────────────────────────

@router.post("/competitors/{competitor_id}/check")
@limiter.limit("10/minute")
def check_competitor_prices(
    request: Request,
    competitor_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually check for price changes on a specific competitor.
    Returns any alerts that would be triggered.
    """
    user_id = current_user["sub"]
    
    # Verify competitor belongs to user
    competitors = db.get_competitors(user_id)
    competitor = next((c for c in competitors if c.get("id") == competitor_id), None)
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    # Check for price changes
    alerts = check_price_changes(user_id, competitor_id)
    
    return {
        "competitor_id": competitor_id,
        "competitor_name": competitor.get("name", "Unknown"),
        "alerts_detected": len(alerts),
        "alerts": alerts
    }
