"""
Buffer service — social media automation for RivalEdge.

Based on Nathan's WatchDeck implementation.
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

BUFFER_API_KEY = os.environ.get("BUFFER_API_KEY", "")
BUFFER_BASE_URL = "https://api.buffer.com"


def _get_headers() -> dict:
    """Get headers for Buffer API (mimics browser context)."""
    api_key = os.environ.get("BUFFER_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://publish.buffer.com",
        "Referer": "https://publish.buffer.com/",
    }


def _make_request(query: str) -> dict:
    """Make GraphQL request to Buffer API."""
    api_key = os.environ.get("BUFFER_API_KEY", "")
    if not api_key:
        raise RuntimeError("BUFFER_API_KEY not set")
    
    payload = json.dumps({"query": query}).encode()
    headers = _get_headers()
    
    try:
        response = httpx.post(
            BUFFER_BASE_URL,
            headers=headers,
            content=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Buffer API error: {e}")
        raise


def get_channels() -> list[dict]:
    """
    Get all connected channels (Twitter, LinkedIn, etc.)
    
    Returns list of channels with id, name, platform, etc.
    """
    query = """query {
        account {
            organizations {
                channels {
                    id
                    name
                    platform
                    username
                }
            }
        }
    }"""
    
    result = _make_request(query)
    channels = []
    
    orgs = result.get("data", {}).get("account", {}).get("organizations", [])
    for org in orgs:
        for channel in org.get("channels", []):
            channels.append(channel)
    
    return channels


def get_last_scheduled(channel_id: str) -> Optional[datetime]:
    """
    Get the latest scheduled post time for a channel.
    Used to compute next available slot.
    """
    # Get organization ID from channels first
    channels = get_channels()
    org_id = None
    for ch in channels:
        if ch["id"] == channel_id:
            # Need to find org ID - fetch from account
            break
    
    # Query posts for this channel
    query = f"""query {{
        posts(input: {{ status: scheduled }}, first: 100) {{
            edges {{
                node {{
                    channelId
                    status
                    dueAt
                }}
            }}
        }}
    }}"""
    
    result = _make_request(query)
    posts = result.get("data", {}).get("posts", {}).get("edges", [])
    
    scheduled = [
        p["node"]["dueAt"]
        for p in posts
        if p["node"]["channelId"] == channel_id and p["node"]["status"] == "scheduled"
    ]
    
    if not scheduled:
        return None
    
    last = sorted(scheduled)[-1]
    return datetime.fromisoformat(last.replace("Z", "+00:00"))


def schedule_post(
    channel_id: str,
    text: str,
    due_at: datetime,
) -> dict:
    """
    Schedule a post to Buffer.
    
    Args:
        channel_id: Buffer channel ID
        text: Post content
        due_at: When to post (UTC)
    
    Returns:
        Post object with id, dueAt, etc.
    """
    due_str = due_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Escape text for GraphQL
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    
    query = f"""mutation {{
        createPost(input: {{
            channelId: "{channel_id}"
            text: "{escaped}"
            schedulingType: automatic
            mode: customScheduled
            dueAt: "{due_str}"
        }}) {{
            ... on PostActionSuccess {{
                __typename
                post {{
                    id
                    dueAt
                    text
                }}
            }}
            ... on MutationError {{
                __typename
                message
            }}
        }}
    }}"""
    
    result = _make_request(query)
    cp = result.get("data", {}).get("createPost", {})
    
    if cp.get("__typename") == "PostActionSuccess":
        return cp["post"]
    
    error_msg = cp.get("message", "Unknown error")
    raise Exception(f"Buffer post creation failed: {error_msg}")


def get_scheduled_posts(channel_id: Optional[str] = None) -> list[dict]:
    """
    Get all scheduled posts.
    
    Optionally filter by channel_id.
    """
    query = """query {
        posts(input: { status: scheduled }, first: 100) {
            edges {
                node {
                    id
                    channelId
                    text
                    dueAt
                    status
                }
            }
        }
    }"""
    
    result = _make_request(query)
    posts = result.get("data", {}).get("posts", {}).get("edges", [])
    
    scheduled = []
    for p in posts:
        post = p["node"]
        if channel_id and post["channelId"] != channel_id:
            continue
        scheduled.append(post)
    
    return sorted(scheduled, key=lambda x: x["dueAt"])


def delete_post(post_id: str) -> bool:
    """Delete a scheduled post."""
    query = f"""mutation {{
        deletePost(input: {{ id: "{post_id}" }}) {{
            ... on DeletePostSuccess {{
                __typename
                success
            }}
            ... on VoidMutationError {{
                __typename
                message
            }}
        }}
    }}"""
    
    result = _make_request(query)
    dp = result.get("data", {}).get("deletePost", {})
    
    return dp.get("__typename") == "DeletePostSuccess"
