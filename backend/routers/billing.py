"""
Billing router — Stripe checkout, portal, and subscription status.
"""
import logging
import os

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from auth import get_current_user
from rate_limit import limiter
import db.supabase as db

logger = logging.getLogger(__name__)

router = APIRouter()

# Configure Stripe key at import time (or lazily — safe either way)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

# Price ID → plan name mapping
PRICE_TO_PLAN = {
    os.environ.get("STRIPE_SOLO_PRICE_ID", "price_1TEYfGLTMdu9rJFPT4iwohw9"): "solo",
    os.environ.get("STRIPE_PRO_PRICE_ID", "price_1TEa3lLTMdu9rJFPgvechLBX"): "pro",
}

PLAN_TO_PRICE = {v: k for k, v in PRICE_TO_PLAN.items()}

# Competitor limits by plan
PLAN_LIMITS = {
    "solo": 3,
    "pro": 10,
}


# ── Schemas ────────────────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    plan: str  # "solo" | "pro"


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


class BillingStatusResponse(BaseModel):
    plan: str
    status: str  # "active" | "inactive"
    competitor_limit: int


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/checkout", response_model=CheckoutResponse)
@limiter.limit("5/hour")
def create_checkout(
    request: Request,
    body: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a Stripe Checkout Session for a subscription plan.
    Returns the hosted checkout URL.
    """
    if body.plan not in PLAN_TO_PRICE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{body.plan}'. Must be one of: {list(PLAN_TO_PRICE)}",
        )

    user_id = current_user["sub"]
    user_email = current_user.get("email", "")

    price_id = PLAN_TO_PRICE[body.plan]

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            subscription_data={"trial_period_days": 14},
            success_url="https://rivaledge.ai/dashboard?checkout=success",
            cancel_url="https://rivaledge.ai/pricing",
            customer_email=user_email or None,
            metadata={"user_id": user_id},
        )
        return CheckoutResponse(checkout_url=session.url)
    except stripe.StripeError as exc:
        logger.error("Stripe checkout error for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider error. Please try again.",
        )


@router.post("/portal", response_model=PortalResponse)
def create_portal(current_user: dict = Depends(get_current_user)):
    """
    Create a Stripe Customer Portal session so the user can manage their subscription.
    Requires the user to have an existing Stripe customer ID.
    """
    user_id = current_user["sub"]

    customer_id = db.get_user_stripe_customer_id(user_id)
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found. Please subscribe first.",
        )

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url="https://rivaledge.ai/dashboard",
        )
        return PortalResponse(portal_url=portal_session.url)
    except stripe.StripeError as exc:
        logger.error("Stripe portal error for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider error. Please try again.",
        )


@router.get("/status", response_model=BillingStatusResponse)
def get_billing_status(current_user: dict = Depends(get_current_user)):
    """Return the current subscription plan and competitor limit for the user."""
    user_id = current_user["sub"]
    user = db.get_user(user_id)

    # If user not in DB yet (Clerk webhook not fired), default to solo plan
    if not user:
        plan = "solo"
    else:
        plan = user.get("plan", "solo")
    # A user record exists → they're active (free tier counts as active)
    sub_status = "active"
    competitor_limit = PLAN_LIMITS.get(plan, 3)

    return BillingStatusResponse(
        plan=plan,
        status=sub_status,
        competitor_limit=competitor_limit,
    )
