"""
Slack Alert System for Competitive Intelligence

Sends real-time CI alerts, ARS changes, and weekly summaries
directly to Slack channels.
"""

import os
import json
import logging
from typing import Optional
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")

# ── Alert Formatters ─────────────────────────────────────────────────────────

def format_competitor_move_alert(alert_data: dict) -> dict:
    """Format competitor move alert for Slack."""
    competitor = alert_data.get("competitor_name", "Unknown")
    move_type = alert_data.get("move_type", "update")
    impact = alert_data.get("impact", "medium")
    details = alert_data.get("details", "")
    url = alert_data.get("url", "")
    
    impact_emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(impact, "ℹ️")
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{impact_emoji} Competitor Alert: {competitor}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Competitor:*\n{competitor}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Move Type:*\n{move_type.title()}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Impact:*\n{impact.upper()}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Detected:*\n{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Details:*\n{details}"
            }
        }
    ]
    
    if url:
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View in RivalEdge",
                        "emoji": True
                    },
                    "url": url,
                    "style": "primary"
                }
            ]
        })
    
    return {"blocks": blocks}


def format_ars_change_alert(alert_data: dict) -> dict:
    """Format ARS change alert for Slack."""
    brand_name = alert_data.get("brand_name", "Your Brand")
    old_ars = alert_data.get("old_ars", 0)
    new_ars = alert_data.get("new_ars", 0)
    change = new_ars - old_ars
    category = alert_data.get("category", "")
    
    trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
    trend_color = "#22c55e" if change > 0 else "#ef4444" if change < 0 else "#6b7280"
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{trend_emoji} AI Recommendation Share Update",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Brand:*\n{brand_name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Category:*\n{category}"
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Previous ARS:*\n{old_ars}%"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Current ARS:*\n*{new_ars}%*"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Change:*\n{'+' if change > 0 else ''}{change:.1f}%"
                }
            ]
        }
    ]
    
    # Add competitor movers if available
    movers = alert_data.get("competitor_movers", [])
    if movers:
        mover_text = "*Competitor Movers:*\n"
        for mover in movers:
            name = mover.get("name", "Unknown")
            m_change = mover.get("change", 0)
            m_emoji = "🟢" if m_change > 0 else "🔴" if m_change < 0 else "⚪"
            mover_text += f"{m_emoji} {name}: {'+' if m_change > 0 else ''}{m_change:.1f}%\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": mover_text
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Dashboard",
                    "emoji": True
                },
                "url": f"https://rivaledge.ai/dashboard?ars={brand_name}",
                "style": "primary"
            }
        ]
    })
    
    return {"blocks": blocks, "attachments": [{"color": trend_color}]}


def format_query_opportunity_alert(alert_data: dict) -> dict:
    """Format query opportunity alert for Slack."""
    query = alert_data.get("query", "")
    search_volume = alert_data.get("search_volume", "medium")
    current_winners = alert_data.get("current_winners", [])
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "💡 Query Opportunity Discovered",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Query:*\n>{query}"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Search Volume:*\n{search_volume.title()}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Your Status:*\n❌ Not mentioned"
                }
            ]
        }
    ]
    
    if current_winners:
        winner_text = "*Current Winners:*\n"
        for i, winner in enumerate(current_winners[:3], 1):
            winner_text += f"{i}. {winner.get('name', 'Unknown')} ({winner.get('mentions', 0)}/10 responses)\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": winner_text
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create Content",
                    "emoji": True
                },
                "url": f"https://rivaledge.ai/dashboard/opportunities?query={query}",
                "style": "primary"
            }
        ]
    })
    
    return {"blocks": blocks}


def format_weekly_summary(alert_data: dict) -> dict:
    """Format weekly CI summary for Slack."""
    brand_name = alert_data.get("brand_name", "Your Brand")
    ars_score = alert_data.get("ars_score", 0)
    ars_change = alert_data.get("ars_change", 0)
    rank = alert_data.get("rank", 0)
    total_competitors = alert_data.get("total_competitors", 0)
    competitor_moves = alert_data.get("competitor_moves", [])
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📈 Weekly CI Summary: {brand_name}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*AI Recommendation Share:*\n{ars_score}% ({'+' if ars_change > 0 else ''}{ars_change:.1f}%)"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Category Rank:*\n#{rank} of {total_competitors}"
                }
            ]
        }
    ]
    
    if competitor_moves:
        moves_text = "*Top Competitor Moves:*\n"
        for move in competitor_moves[:3]:
            name = move.get("competitor_name", "Unknown")
            m_type = move.get("move_type", "update")
            impact = move.get("impact", "medium")
            emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(impact, "ℹ️")
            moves_text += f"{emoji} {name}: {m_type.title()}\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": moves_text
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Full Report",
                    "emoji": True
                },
                "url": "https://rivaledge.ai/dashboard",
                "style": "primary"
            }
        ]
    })
    
    return {"blocks": blocks}


def format_ai_drift_alert(alert_data: dict) -> dict:
    """Format AI competitive drift alert for Slack."""
    competitor = alert_data.get("competitor_name", "Unknown")
    platform = alert_data.get("platform", "ChatGPT")
    old_framing = alert_data.get("old_framing", "")
    new_framing = alert_data.get("new_framing", "")
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "⚠️ AI Competitive Drift Detected",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Competitor:*\n{competitor}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Platform:*\n{platform}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Previous Framing:*\n_{old_framing}_"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Current Framing:*\n*{new_framing}*"
            }
        }
    ]
    
    return {"blocks": blocks, "attachments": [{"color": "#f59e0b"}]}


# ── Slack API Client ─────────────────────────────────────────────────────────

class SlackClient:
    """Client for sending messages to Slack."""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or SLACK_BOT_TOKEN
        self.base_url = "https://slack.com/api"
    
    async def send_message(self, channel: str, message: dict) -> dict:
        """Send a message to a Slack channel."""
        if not self.bot_token:
            logger.error("Slack bot token not configured")
            return {"ok": False, "error": "Bot token not configured"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat.postMessage",
                    headers={
                        "Authorization": f"Bearer {self.bot_token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "channel": channel,
                        **message,
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("ok"):
                    logger.error(f"Slack API error: {data.get('error')}")
                
                return data
            except Exception as e:
                logger.error(f"Failed to send Slack message: {e}")
                return {"ok": False, "error": str(e)}
    
    async def send_alert(self, channel: str, alert_type: str, alert_data: dict) -> dict:
        """Send a formatted alert to Slack."""
        formatters = {
            "competitor_move": format_competitor_move_alert,
            "ars_change": format_ars_change_alert,
            "query_opportunity": format_query_opportunity_alert,
            "weekly_summary": format_weekly_summary,
            "ai_drift": format_ai_drift_alert,
        }
        
        formatter = formatters.get(alert_type)
        if not formatter:
            logger.error(f"Unknown alert type: {alert_type}")
            return {"ok": False, "error": f"Unknown alert type: {alert_type}"}
        
        message = formatter(alert_data)
        return await self.send_message(channel, message)


# ── User Configuration ───────────────────────────────────────────────────────

def get_user_slack_config(user_id: str) -> dict:
    """Get Slack configuration for a user."""
    import db.supabase as db
    
    try:
        r = httpx.get(
            db._url(f"slack_configs?user_id=eq.{user_id}&limit=1"),
            headers=db._headers(),
            timeout=10,
        )
        
        if r.status_code >= 400:
            return {}
        
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return {}
    except Exception as e:
        logger.error(f"Failed to get Slack config: {e}")
        return {}


def save_slack_config(user_id: str, config: dict) -> dict:
    """Save Slack configuration for a user."""
    import db.supabase as db
    
    payload = {
        "user_id": user_id,
        "workspace_id": config.get("workspace_id"),
        "channel_id": config.get("channel_id"),
        "channel_name": config.get("channel_name"),
        "alert_types": config.get("alert_types", ["competitor_move", "ars_change"]),
        "is_active": config.get("is_active", True),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    try:
        # Upsert configuration
        headers = {**db._headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
        r = httpx.post(
            db._url("slack_configs"),
            json=payload,
            headers=headers,
            timeout=10,
        )
        
        if r.status_code >= 400:
            logger.error(f"Failed to save Slack config: {r.text[:500]}")
            return {}
        
        data = r.json()
        return data[0] if isinstance(data, list) and data else payload
    except Exception as e:
        logger.error(f"Failed to save Slack config: {e}")
        return {}


# ── Alert Triggers ───────────────────────────────────────────────────────────

async def trigger_competitor_move_alert(user_id: str, competitor_data: dict):
    """Trigger a competitor move alert for a user."""
    config = get_user_slack_config(user_id)
    if not config or not config.get("is_active"):
        return
    
    alert_types = config.get("alert_types", [])
    if "competitor_move" not in alert_types:
        return
    
    client = SlackClient()
    await client.send_alert(
        channel=config["channel_id"],
        alert_type="competitor_move",
        alert_data=competitor_data,
    )


async def trigger_ars_change_alert(user_id: str, ars_data: dict):
    """Trigger an ARS change alert for a user."""
    config = get_user_slack_config(user_id)
    if not config or not config.get("is_active"):
        return
    
    alert_types = config.get("alert_types", [])
    if "ars_change" not in alert_types:
        return
    
    client = SlackClient()
    await client.send_alert(
        channel=config["channel_id"],
        alert_type="ars_change",
        alert_data=ars_data,
    )


async def trigger_weekly_summary(user_id: str, summary_data: dict):
    """Trigger weekly summary for a user."""
    config = get_user_slack_config(user_id)
    if not config or not config.get("is_active"):
        return
    
    alert_types = config.get("alert_types", [])
    if "weekly_summary" not in alert_types:
        return
    
    client = SlackClient()
    await client.send_alert(
        channel=config["channel_id"],
        alert_type="weekly_summary",
        alert_data=summary_data,
    )


# ── Export ───────────────────────────────────────────────────────────────────

__all__ = [
    "SlackClient",
    "get_user_slack_config",
    "save_slack_config",
    "trigger_competitor_move_alert",
    "trigger_ars_change_alert",
    "trigger_weekly_summary",
]
