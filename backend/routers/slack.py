"""
Slack Integration Router

API endpoints for configuring and testing Slack integrations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from auth import get_current_user, resolve_db_id
from services.slack_alerts import (
    SlackClient,
    get_user_slack_config,
    save_slack_config,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class SlackConfigRequest(BaseModel):
    workspace_id: str = Field(..., min_length=1)
    channel_id: str = Field(..., min_length=1)
    channel_name: str = Field(..., min_length=1)
    alert_types: list[str] = Field(default=["competitor_move", "ars_change"])


class SlackTestRequest(BaseModel):
    message: str = Field(default="🎯 This is a test alert from RivalEdge CI!")


class SlackConfigResponse(BaseModel):
    id: str
    user_id: str
    workspace_id: str
    channel_id: str
    channel_name: str
    alert_types: list[str]
    is_active: bool
    created_at: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/config", response_model=Optional[SlackConfigResponse])
def get_slack_config(current_user: dict = Depends(get_current_user)):
    """Get Slack configuration for the authenticated user."""
    user_id = resolve_db_id(current_user)
    config = get_user_slack_config(user_id)
    
    if not config:
        return None
    
    return SlackConfigResponse(
        id=config.get("id", ""),
        user_id=config.get("user_id", ""),
        workspace_id=config.get("workspace_id", ""),
        channel_id=config.get("channel_id", ""),
        channel_name=config.get("channel_name", ""),
        alert_types=config.get("alert_types", []),
        is_active=config.get("is_active", True),
        created_at=config.get("created_at", ""),
    )


@router.post("/config", response_model=SlackConfigResponse)
def configure_slack(
    body: SlackConfigRequest,
    current_user: dict = Depends(get_current_user),
):
    """Configure Slack integration for the authenticated user."""
    user_id = resolve_db_id(current_user)
    
    # Validate alert types
    valid_types = {"competitor_move", "ars_change", "query_opportunity", "weekly_summary", "ai_drift"}
    invalid_types = set(body.alert_types) - valid_types
    if invalid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alert types: {invalid_types}",
        )
    
    config = save_slack_config(user_id, body.dict())
    
    return SlackConfigResponse(
        id=config.get("id", ""),
        user_id=config.get("user_id", ""),
        workspace_id=config.get("workspace_id", ""),
        channel_id=config.get("channel_id", ""),
        channel_name=config.get("channel_name", ""),
        alert_types=config.get("alert_types", []),
        is_active=config.get("is_active", True),
        created_at=config.get("created_at", ""),
    )


@router.post("/test")
async def test_slack_integration(
    body: SlackTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send a test message to the configured Slack channel."""
    user_id = resolve_db_id(current_user)
    config = get_user_slack_config(user_id)
    
    if not config or not config.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slack integration not configured. Use POST /config first.",
        )
    
    client = SlackClient()
    result = await client.send_message(
        channel=config["channel_id"],
        message={
            "text": body.message,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": body.message
                    }
                }
            ]
        }
    )
    
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test message: {result.get('error', 'Unknown error')}",
        )
    
    return {"status": "ok", "message": "Test message sent successfully"}


@router.delete("/config")
def delete_slack_config(current_user: dict = Depends(get_current_user)):
    """Delete Slack configuration for the authenticated user."""
    user_id = resolve_db_id(current_user)
    
    import db.supabase as db
    import httpx
    
    try:
        r = httpx.delete(
            db._url(f"slack_configs?user_id=eq.{user_id}"),
            headers=db._headers(),
            timeout=10,
        )
        
        if r.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete Slack configuration",
            )
        
        return {"status": "ok", "message": "Slack configuration deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete configuration: {str(e)}",
        )


@router.get("/alert-types")
def get_alert_types():
    """Get available alert types for Slack integration."""
    return {
        "alert_types": [
            {
                "id": "competitor_move",
                "name": "Competitor Move Alerts",
                "description": "Get notified when competitors make significant moves (pricing changes, feature launches, etc.)",
            },
            {
                "id": "ars_change",
                "name": "AI Recommendation Share Changes",
                "description": "Get notified when your AI Recommendation Share changes significantly",
            },
            {
                "id": "query_opportunity",
                "name": "Query Opportunities",
                "description": "Get notified when new high-value AI search queries are discovered",
            },
            {
                "id": "weekly_summary",
                "name": "Weekly Summary",
                "description": "Receive a weekly summary of competitive intelligence and AI visibility",
            },
            {
                "id": "ai_drift",
                "name": "AI Competitive Drift",
                "description": "Get notified when AI platforms change how they frame your competitors",
            },
        ]
    }
