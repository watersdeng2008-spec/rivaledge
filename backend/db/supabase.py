"""
Supabase database operations using raw HTTP — no client library.
Avoids supabase-py version incompatibilities across environments.
"""
import os
import httpx
from typing import Optional


def _headers() -> dict:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _url(path: str) -> str:
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    return f"{base}/rest/v1/{path}"


def get_user(user_id: str) -> Optional[dict]:
    r = httpx.get(_url(f"users?id=eq.{user_id}&limit=1"), headers=_headers(), timeout=10)
    data = r.json()
    return data[0] if isinstance(data, list) and data else None


def upsert_user(user_id: str, email: str = "", plan: str = "solo") -> dict:
    payload = {"id": user_id, "email": email or f"{user_id}@unknown.local", "plan": plan}
    headers = {**_headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
    r = httpx.post(_url("users"), json=payload, headers=headers, timeout=10)
    data = r.json()
    return data[0] if isinstance(data, list) and data else payload


def get_competitors(user_id: str) -> list:
    r = httpx.get(
        _url(f"competitors?user_id=eq.{user_id}&order=created_at.desc"),
        headers=_headers(), timeout=10
    )
    data = r.json()
    return data if isinstance(data, list) else []


def create_competitor(user_id: str, url: str, name: Optional[str] = None) -> dict:
    payload = {"user_id": user_id, "url": url, "name": name}
    r = httpx.post(_url("competitors"), json=payload, headers=_headers(), timeout=10)
    data = r.json()
    if isinstance(data, list) and data:
        return data[0]
    # Fetch back if insert didn't return data
    fetch = httpx.get(
        _url(f"competitors?user_id=eq.{user_id}&url=eq.{url}&order=created_at.desc&limit=1"),
        headers=_headers(), timeout=10
    )
    rows = fetch.json()
    return rows[0] if isinstance(rows, list) and rows else {**payload, "id": "pending", "profile": None, "created_at": ""}


def delete_competitor(competitor_id: str, user_id: str) -> bool:
    httpx.delete(
        _url(f"competitors?id=eq.{competitor_id}&user_id=eq.{user_id}"),
        headers=_headers(), timeout=10
    )
    return True


def get_competitor_snapshots(competitor_id: str, limit: int = 12) -> list:
    r = httpx.get(
        _url(f"snapshots?competitor_id=eq.{competitor_id}&order=created_at.desc&limit={limit}"),
        headers=_headers(), timeout=10
    )
    data = r.json()
    return data if isinstance(data, list) else []


def create_snapshot(competitor_id: str, content: dict, diff: Optional[dict] = None) -> dict:
    import json
    payload = {"competitor_id": competitor_id, "content": content, "diff": diff}
    r = httpx.post(_url("snapshots"), json=payload, headers=_headers(), timeout=10)
    data = r.json()
    return data[0] if isinstance(data, list) and data else payload


def get_latest_snapshot(competitor_id: str) -> Optional[dict]:
    r = httpx.get(
        _url(f"snapshots?competitor_id=eq.{competitor_id}&order=created_at.desc&limit=1"),
        headers=_headers(), timeout=10
    )
    data = r.json()
    return data[0] if isinstance(data, list) and data else None


def get_prior_snapshot(competitor_id: str) -> Optional[dict]:
    r = httpx.get(
        _url(f"snapshots?competitor_id=eq.{competitor_id}&order=created_at.desc&limit=2"),
        headers=_headers(), timeout=10
    )
    data = r.json()
    return data[1] if isinstance(data, list) and len(data) > 1 else None


def create_digest(user_id: str, content: str) -> dict:
    payload = {"user_id": user_id, "content": content}
    r = httpx.post(_url("digests"), json=payload, headers=_headers(), timeout=10)
    data = r.json()
    return data[0] if isinstance(data, list) and data else payload


def mark_digest_sent(digest_id: str) -> bool:
    return update_digest_sent(digest_id)


def get_digest(digest_id: str, user_id: str = None) -> Optional[dict]:
    r = httpx.get(_url(f"digests?id=eq.{digest_id}&limit=1"), headers=_headers(), timeout=10)
    data = r.json()
    return data[0] if isinstance(data, list) and data else None


def update_digest_sent(digest_id: str) -> bool:
    from datetime import datetime, timezone
    payload = {"sent_at": datetime.now(timezone.utc).isoformat()}
    httpx.patch(_url(f"digests?id=eq.{digest_id}"), json=payload, headers=_headers(), timeout=10)
    return True


def get_all_active_users() -> list:
    r = httpx.get(_url("users?select=*"), headers=_headers(), timeout=10)
    data = r.json()
    return data if isinstance(data, list) else []


def update_user_plan(user_id: str, plan: str) -> bool:
    httpx.patch(_url(f"users?id=eq.{user_id}"), json={"plan": plan}, headers=_headers(), timeout=10)
    return True


def get_user_stripe_customer_id(user_id: str) -> Optional[str]:
    user = get_user(user_id)
    return user.get("stripe_customer_id") if user else None


def update_user_stripe_customer_id(user_id: str, customer_id: str) -> bool:
    httpx.patch(_url(f"users?id=eq.{user_id}"), json={"stripe_customer_id": customer_id}, headers=_headers(), timeout=10)
    return True


# ── Sales Analytics Tables ────────────────────────────────────────────────────

def get_sales_agent_logs(since: Optional[str] = None, limit: int = 100) -> list:
    """Get sales agent run logs, optionally filtered by a start timestamp."""
    path = "sales_agent_logs?order=started_at.desc"
    if since:
        path += f"&started_at=gte.{since}"
    if limit:
        path += f"&limit={limit}"
    r = httpx.get(_url(path), headers=_headers(), timeout=10)
    data = r.json()
    return data if isinstance(data, list) else []


def get_sales_leads(since: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> list:
    """Get sales leads, optionally filtered by creation date and/or status."""
    path = "sales_leads?order=created_at.desc"
    if since:
        path += f"&created_at=gte.{since}"
    if status:
        path += f"&status=eq.{status}"
    if limit:
        path += f"&limit={limit}"
    r = httpx.get(_url(path), headers=_headers(), timeout=10)
    data = r.json()
    return data if isinstance(data, list) else []


def get_sales_leads_by_statuses(statuses: list, limit: int = 10) -> list:
    """Get sales leads whose status is one of the provided values (PostgREST `in` filter)."""
    status_list = ",".join(statuses)
    path = f"sales_leads?status=in.({status_list})&order=reply_received_at.desc&limit={limit}"
    r = httpx.get(_url(path), headers=_headers(), timeout=10)
    data = r.json()
    return data if isinstance(data, list) else []


def update_sales_lead(lead_id: str, update_data: dict) -> Optional[dict]:
    """Update a sales lead by ID."""
    r = httpx.patch(_url(f"sales_leads?id=eq.{lead_id}"), json=update_data, headers=_headers(), timeout=10)
    data = r.json()
    return data[0] if isinstance(data, list) and data else None


def get_sales_performance(limit: int = 100) -> list:
    """Get sales performance records ordered by reply rate descending."""
    path = f"sales_performance?order=reply_rate.desc&limit={limit}"
    r = httpx.get(_url(path), headers=_headers(), timeout=10)
    data = r.json()
    return data if isinstance(data, list) else []
