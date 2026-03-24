"""
Supabase client — singleton pattern.
All DB operations go through this module.
"""
import os
from typing import Optional
from supabase import create_client, Client

_client: Optional[Client] = None


def get_client() -> Client:
    """Return (or lazily create) the Supabase client."""
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _client = create_client(url, key)
    return _client


# ── Convenience helpers ────────────────────────────────────────────────────────

def get_user(user_id: str) -> Optional[dict]:
    """Fetch a user record by Clerk user ID."""
    client = get_client()
    result = client.table("users").select("*").eq("id", user_id).single().execute()
    return result.data


def upsert_user(user_id: str, email: str, plan: str = "solo") -> dict:
    """Create or update a user record."""
    client = get_client()
    result = (
        client.table("users")
        .upsert({"id": user_id, "email": email, "plan": plan})
        .execute()
    )
    return result.data[0]


def get_competitors(user_id: str) -> list[dict]:
    """List all competitors for a user."""
    client = get_client()
    result = (
        client.table("competitors")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def create_competitor(user_id: str, url: str, name: Optional[str] = None) -> dict:
    """Add a new competitor to track."""
    client = get_client()
    result = (
        client.table("competitors")
        .insert({"user_id": user_id, "url": url, "name": name})
        .execute()
    )
    return result.data[0]


def delete_competitor(competitor_id: str, user_id: str) -> bool:
    """Delete a competitor (user-scoped for safety)."""
    client = get_client()
    client.table("competitors").delete().eq("id", competitor_id).eq(
        "user_id", user_id
    ).execute()
    return True


def create_snapshot(competitor_id: str, content: dict, diff: Optional[dict] = None) -> dict:
    """Store a new snapshot for a competitor."""
    client = get_client()
    result = (
        client.table("snapshots")
        .insert({"competitor_id": competitor_id, "content": content, "diff": diff})
        .execute()
    )
    return result.data[0]


def get_latest_snapshot(competitor_id: str) -> Optional[dict]:
    """Get the most recent snapshot for a competitor."""
    client = get_client()
    result = (
        client.table("snapshots")
        .select("*")
        .eq("competitor_id", competitor_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def get_prior_snapshot(competitor_id: str) -> Optional[dict]:
    """Get the second-most-recent snapshot for a competitor (for diff comparison)."""
    client = get_client()
    result = (
        client.table("snapshots")
        .select("*")
        .eq("competitor_id", competitor_id)
        .order("created_at", desc=True)
        .limit(2)
        .execute()
    )
    return result.data[1] if result.data and len(result.data) > 1 else None


def get_all_active_users() -> list[dict]:
    """Get all users (for cron job processing)."""
    client = get_client()
    result = client.table("users").select("*").execute()
    return result.data


def get_digest(digest_id: str, user_id: str) -> Optional[dict]:
    """Get a digest by ID, scoped to user for safety."""
    client = get_client()
    result = (
        client.table("digests")
        .select("*")
        .eq("id", digest_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return result.data


def create_digest(user_id: str, content: str) -> dict:
    """Store a new digest record."""
    client = get_client()
    result = (
        client.table("digests")
        .insert({"user_id": user_id, "content": content})
        .execute()
    )
    return result.data[0]


def mark_digest_sent(digest_id: str) -> dict:
    """Mark a digest as sent (sets sent_at to now)."""
    from datetime import datetime, timezone
    client = get_client()
    result = (
        client.table("digests")
        .update({"sent_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", digest_id)
        .execute()
    )
    return result.data[0]
