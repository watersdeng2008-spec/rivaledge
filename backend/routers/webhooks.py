from typing import Optional
"""
Webhooks router — Clerk user sync + Stripe billing events.

Clerk sends webhooks when users are created/updated/deleted.
We sync these to our users table.
"""
import hashlib
import hmac
import json
import logging
import os

import stripe
from fastapi import APIRouter, Header, HTTPException, Request, status

import db.supabase as db

logger = logging.getLogger(__name__)

# Price ID → plan name mapping (mirrors billing.py — single source of truth in env)
_PRICE_TO_PLAN = {
    os.environ.get("STRIPE_SOLO_PRICE_ID", "price_1TEYfGLTMdu9rJFPT4iwohw9"): "solo",
    os.environ.get("STRIPE_PRO_PRICE_ID", "price_1TEa3lLTMdu9rJFPgvechLBX"): "pro",
}

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
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    """
    Receive and verify Stripe billing events.

    Events handled:
      - checkout.session.completed → update user plan + store customer ID
      - customer.subscription.updated → update plan if price changed
      - customer.subscription.deleted → downgrade to 'solo'
      - invoice.payment_failed → log warning
    """
    payload = await request.body()
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    # Verify Stripe webhook signature — never trust unverified webhooks
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature or "",
            secret=webhook_secret,
        )
    except Exception as exc:
        logger.warning("Stripe webhook signature verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    event_type = event.type
    obj = event.data.object

    try:
        if event_type == "checkout.session.completed":
            _handle_checkout_completed(obj)

        elif event_type == "customer.subscription.updated":
            _handle_subscription_updated(obj)

        elif event_type == "customer.subscription.deleted":
            _handle_subscription_deleted(obj)

        elif event_type == "invoice.payment_failed":
            customer_id = obj.get("customer")
            logger.warning("Payment failed for Stripe customer %s", customer_id)

        else:
            logger.debug("Unhandled Stripe event: %s", event_type)

    except Exception as exc:
        # Stripe webhook errors should never propagate — always return 200 to Stripe
        logger.error("Error processing Stripe event %s: %s", event_type, exc)

    return {"status": "ok", "event": event_type}


def _get_user_id_from_customer(customer_id: str, metadata: dict) -> Optional[str]:
    """
    Resolve a Clerk user_id from event metadata or Stripe customer lookup.
    Metadata is preferred (set during checkout); customer lookup is a fallback.
    """
    # Prefer metadata set during checkout session creation
    if metadata and metadata.get("user_id"):
        return metadata["user_id"]

    # Fallback: look up by stripe_customer_id in our DB
    # (This path is hit when we receive subscription events without metadata)
    try:
        result = db.get_client().table("users") \
            .select("id") \
            .eq("stripe_customer_id", customer_id) \
            .single() \
            .execute()
        if result.data:
            return result.data["id"]
    except Exception as exc:
        logger.error("Customer lookup failed for %s: %s", customer_id, exc)
    return None


def _handle_checkout_completed(obj: dict) -> None:
    """Handle checkout.session.completed — update plan and store customer ID."""
    customer_id = obj.get("customer")
    metadata = obj.get("metadata") or {}
    user_id = _get_user_id_from_customer(customer_id, metadata)

    if not user_id:
        logger.warning("checkout.session.completed: could not resolve user for customer %s", customer_id)
        return

    # Store customer ID so future events can look up the user
    if customer_id:
        db.update_user_stripe_customer_id(user_id, customer_id)

    # Determine plan from subscription price
    subscription_id = obj.get("subscription")
    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            price_id = subscription["items"]["data"][0]["price"]["id"]
            plan = _PRICE_TO_PLAN.get(price_id, "solo")
            db.update_user_plan(user_id, plan)
            logger.info("User %s upgraded to plan '%s'", user_id, plan)
        except Exception as exc:
            logger.error("Could not retrieve subscription %s: %s", subscription_id, exc)
    else:
        # No subscription in session — default to solo
        db.update_user_plan(user_id, "solo")


def _handle_subscription_updated(obj: dict) -> None:
    """Handle customer.subscription.updated — sync plan change."""
    customer_id = obj.get("customer")
    metadata = obj.get("metadata") or {}
    user_id = _get_user_id_from_customer(customer_id, metadata)

    if not user_id:
        logger.warning("subscription.updated: could not resolve user for customer %s", customer_id)
        return

    try:
        price_id = obj["items"]["data"][0]["price"]["id"]
        plan = _PRICE_TO_PLAN.get(price_id, "solo")
        db.update_user_plan(user_id, plan)
        logger.info("User %s plan updated to '%s'", user_id, plan)
    except (KeyError, IndexError) as exc:
        logger.error("subscription.updated: could not parse price for customer %s: %s", customer_id, exc)


def _handle_subscription_deleted(obj: dict) -> None:
    """Handle customer.subscription.deleted — downgrade user to solo (free tier)."""
    customer_id = obj.get("customer")
    metadata = obj.get("metadata") or {}
    user_id = _get_user_id_from_customer(customer_id, metadata)

    if not user_id:
        logger.warning("subscription.deleted: could not resolve user for customer %s", customer_id)
        return

    db.update_user_plan(user_id, "solo")
    logger.info("User %s downgraded to 'solo' (subscription cancelled)", user_id)
