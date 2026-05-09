"""
Billing router — Stripe checkout, portal, and subscription status.
"""
import logging
import os

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from auth import get_current_user, resolve_db_id
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

# GEO add-on price IDs
GEO_SETUP_PRICE_ID = os.environ.get(
    "STRIPE_GEO_SETUP_PRICE_ID",
    "price_1TV0iyLTMdu9rJFPvdYHpLKT",  # $799 one-time
)
GEO_MONTHLY_PRICE_ID = os.environ.get(
    "STRIPE_GEO_MONTHLY_PRICE_ID",
    "price_1TV0iyLTMdu9rJFP28U5ndtk",  # $299/mo
)

# Competitor limits by plan
PLAN_LIMITS = {
    "solo": 3,
    "pro": 10,
}


# ── Schemas ────────────────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    plan: str  # "solo" | "pro" | "geo" (add-on)


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


class BillingStatusResponse(BaseModel):
    plan: str
    status: str  # "active" | "inactive"
    has_geo_addon: bool = False
    competitor_limit: int
    competitor_count: int = 0


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

    user_id = resolve_db_id(current_user)
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
    user_id = resolve_db_id(current_user)

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


@router.post("/addon-checkout", response_model=CheckoutResponse)
@limiter.limit("5/hour")
def create_addon_checkout(
    request: Request,
    body: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a Stripe Checkout Session for the GEO add-on.
    Includes $799 one-time setup + $299/mo subscription in one session.
    User must already be on a paid plan (Solo or Pro).
    """
    if body.plan not in ("solo", "pro", "geo"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{body.plan}'.",
        )

    user_id = resolve_db_id(current_user)
    user_email = current_user.get("email", "")

    # For GEO add-on, user should already be on a paid plan (check is best-effort)
    user = db.get_user(user_id)
    current_plan = user.get("plan") if user else None
    if body.plan == "geo" and current_plan not in ("solo", "pro"):
        logger.warning(
            "GEO add-on checkout for user %s without active paid plan (plan=%s) — allowing anyway",
            user_id, current_plan,
        )
        # Don't block — Stripe payment is the real gate

    try:
        if body.plan == "geo":
            # GEO add-on: $799 setup fee + $299/mo subscription
            # Create/get Stripe customer to attach one-time setup invoice item
            customers = stripe.Customer.list(email=user_email, limit=1)
            if customers.data:
                customer_id = customers.data[0].id
            else:
                customer = stripe.Customer.create(
                    email=user_email,
                    metadata={"user_id": user_id},
                )
                customer_id = customer.id

            # Add $799 one-time setup fee as invoice item (added to first subscription invoice)
            stripe.InvoiceItem.create(
                customer=customer_id,
                price=GEO_SETUP_PRICE_ID,
            )

            session = stripe.checkout.Session.create(
                mode="subscription",
                payment_method_types=["card"],
                line_items=[
                    {"price": GEO_MONTHLY_PRICE_ID, "quantity": 1},  # $299/mo
                ],
                subscription_data={"trial_period_days": 0},
                success_url="https://rivaledge.ai/dashboard?addon=geo_success",
                cancel_url="https://rivaledge.ai/pricing",
                customer=customer_id,
                metadata={
                    "user_id": user_id,
                    "addon": "geo",
                },
            )
        else:
            # Standard plan checkout
            price_id = PLAN_TO_PRICE[body.plan]
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


@router.get("/status", response_model=BillingStatusResponse)
def get_billing_status(current_user: dict = Depends(get_current_user)):
    """Return the current subscription plan and competitor limit for the user."""
    user_id = resolve_db_id(current_user)
    user = db.get_user(user_id)

    logger.info("billing_status: user_id=%s, db_result=%s", user_id, user.get("plan") if user else "NOT_FOUND")

    # If user not in DB yet, default to solo plan
    if not user:
        plan = "solo"
        has_geo = False
    else:
        plan = user.get("plan") or "solo"
        has_geo = user.get("has_geo_addon", False)
    sub_status = "active"
    competitor_limit = PLAN_LIMITS.get(plan, 3)

    # Count actual competitors
    competitors = db.get_competitors(user_id)
    competitor_count = len(competitors) if competitors else 0

    return {
        "plan": plan,
        "status": sub_status,
        "has_geo_addon": has_geo,
        "competitor_limit": competitor_limit,
        "competitor_count": competitor_count,
    }
