"""
Webhooks router — Clerk user sync + Stripe billing events.

Clerk sends webhooks when users are created/updated/deleted.
We sync these to our users table.
"""
import hashlib
import hmac
import json
import os

from fastapi import APIRouter, Header, HTTPException, Request, status

import db.supabase as db

router = APIRouter()


def _verify_clerk_webhook(payload: bytes, svix_id: str, svix_timestamp: str, svix_signature: str) -> bool:
    """
    Verify Clerk webhook signature using svix.
    See: https://docs.svix.com/receiving/verifying-payloads/how-manual
    """
    secret = os.environ.get("CLERK_WEBHOOK_SECRET", "")
    if not secret:
        return False

    # Svix signature format: "v1,<base64>"
    signed_content = f"{svix_id}.{svix_timestamp}.{payload.decode('utf-8')}"
    
    # Remove "whsec_" prefix if present
    if secret.startswith("whsec_"):
        import base64
        secret_bytes = base64.b64decode(secret[6:])
    else:
        secret_bytes = secret.encode()
    
    expected = hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    import base64
    expected_b64 = base64.b64encode(expected).decode()
    
    # svix_signature may contain multiple signatures (space-separated v1,<sig>)
    for sig in svix_signature.split(" "):
        if sig.startswith("v1,") and hmac.compare_digest(sig[3:], expected_b64):
            return True
    return False


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    svix_id: str = Header(None, alias="svix-id"),
    svix_timestamp: str = Header(None, alias="svix-timestamp"),
    svix_signature: str = Header(None, alias="svix-signature"),
):
    """
    Receive Clerk user lifecycle events and sync to Supabase.
    Events handled: user.created, user.updated, user.deleted
    """
    payload = await request.body()
    
    # Verify webhook signature (skip in dev if secret not set)
    webhook_secret = os.environ.get("CLERK_WEBHOOK_SECRET", "")
    if webhook_secret and svix_id and svix_timestamp and svix_signature:
        if not _verify_clerk_webhook(payload, svix_id, svix_timestamp, svix_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )
    
    data = json.loads(payload)
    event_type = data.get("type")
    event_data = data.get("data", {})
    
    if event_type == "user.created":
        user_id = event_data["id"]
        email_addresses = event_data.get("email_addresses", [])
        email = email_addresses[0]["email_address"] if email_addresses else ""
        db.upsert_user(user_id=user_id, email=email)
        return {"status": "user created", "user_id": user_id}
    
    elif event_type == "user.updated":
        user_id = event_data["id"]
        email_addresses = event_data.get("email_addresses", [])
        email = email_addresses[0]["email_address"] if email_addresses else ""
        db.upsert_user(user_id=user_id, email=email)
        return {"status": "user updated", "user_id": user_id}
    
    elif event_type == "user.deleted":
        # Cascade delete handled by DB foreign keys
        return {"status": "user deleted (cascade)"}
    
    # Unknown event — log and ack
    return {"status": "ignored", "event": event_type}


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Receive Stripe billing events.
    Handles: checkout.session.completed, customer.subscription.updated/deleted
    Day 4 feature — stub for now.
    """
    # TODO: Implement Stripe webhook handling on Day 4
    payload = await request.body()
    data = json.loads(payload)
    event_type = data.get("type", "unknown")
    
    return {"status": "received", "event": event_type}
