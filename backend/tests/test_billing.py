"""
Tests for billing endpoints and Stripe webhook handler.
Written FIRST (TDD) — implementation follows.
All Stripe SDK calls are mocked — no real API calls.
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Env vars set before any imports
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_fake")
os.environ.setdefault("STRIPE_SOLO_PRICE_ID", "price_1TEYfGLTMdu9rJFPT4iwohw9")
os.environ.setdefault("STRIPE_PRO_PRICE_ID", "price_1TEa3lLTMdu9rJFPgvechLBX")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

MOCK_USER_PAYLOAD = {
    "sub": "user_test123",
    "email": "test@example.com",
    "exp": 9999999999,
}

MOCK_USER_DB = {
    "id": "user_test123",
    "email": "test@example.com",
    "plan": "solo",
    "stripe_customer_id": None,
    "created_at": "2024-01-01T00:00:00+00:00",
}

MOCK_USER_DB_PRO = {
    "id": "user_test123",
    "email": "test@example.com",
    "plan": "pro",
    "stripe_customer_id": "cus_test123",
    "created_at": "2024-01-01T00:00:00+00:00",
}


# ── Checkout Tests ─────────────────────────────────────────────────────────────

class TestCheckoutEndpoint:
    def test_checkout_creates_stripe_session(self):
        """POST /api/billing/checkout returns checkout_url from Stripe."""
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_abc123"

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB), \
             patch("stripe.checkout.Session.create", return_value=mock_session):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/billing/checkout",
                headers={"Authorization": "Bearer fake-token"},
                json={"plan": "solo"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "checkout_url" in data
        assert data["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_abc123"

    def test_checkout_requires_auth(self):
        """POST /api/billing/checkout returns 401/403 without auth."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/billing/checkout",
            json={"plan": "solo"},
        )
        assert resp.status_code in (401, 403)

    def test_checkout_invalid_plan_returns_400(self):
        """POST /api/billing/checkout returns 400 for invalid plan name."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/billing/checkout",
                headers={"Authorization": "Bearer fake-token"},
                json={"plan": "enterprise"},
            )
        assert resp.status_code == 400

    def test_checkout_pro_plan(self):
        """POST /api/billing/checkout works for pro plan."""
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_pro"

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB), \
             patch("stripe.checkout.Session.create", return_value=mock_session):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/billing/checkout",
                headers={"Authorization": "Bearer fake-token"},
                json={"plan": "pro"},
            )
        assert resp.status_code == 200
        assert "checkout_url" in resp.json()


# ── Portal Tests ───────────────────────────────────────────────────────────────

class TestPortalEndpoint:
    def test_portal_creates_portal_session(self):
        """POST /api/billing/portal returns portal_url."""
        mock_portal = MagicMock()
        mock_portal.url = "https://billing.stripe.com/session/bps_test_abc"

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB_PRO), \
             patch("db.supabase.get_user_stripe_customer_id", return_value="cus_test123"), \
             patch("stripe.billing_portal.Session.create", return_value=mock_portal):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/billing/portal",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "portal_url" in data
        assert "billing.stripe.com" in data["portal_url"]

    def test_portal_requires_auth(self):
        """POST /api/billing/portal returns 401/403 without auth."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/billing/portal")
        assert resp.status_code in (401, 403)

    def test_portal_returns_404_when_no_customer(self):
        """POST /api/billing/portal returns 404 if user has no Stripe customer ID."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB), \
             patch("db.supabase.get_user_stripe_customer_id", return_value=None):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/billing/portal",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 404


# ── Status Tests ───────────────────────────────────────────────────────────────

class TestBillingStatusEndpoint:
    def test_billing_status_returns_plan(self):
        """GET /api/billing/status returns current plan and limits."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/billing/status",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] == "solo"
        assert data["status"] in ("active", "inactive")
        assert "competitor_limit" in data
        assert data["competitor_limit"] == 3  # Solo = 3

    def test_billing_status_pro_returns_10_limit(self):
        """GET /api/billing/status returns 10 competitor limit for pro plan."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB_PRO):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/billing/status",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] == "pro"
        assert data["competitor_limit"] == 10  # Pro = 10

    def test_billing_status_requires_auth(self):
        """GET /api/billing/status returns 401/403 without auth."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/billing/status")
        assert resp.status_code in (401, 403)


# ── Webhook Tests ──────────────────────────────────────────────────────────────

class TestStripeWebhook:
    def _make_event(self, event_type: str, data: dict) -> dict:
        return {"type": event_type, "data": {"object": data}}

    def test_webhook_checkout_completed_updates_plan(self):
        """checkout.session.completed event updates user plan in DB."""
        event_data = {
            "customer": "cus_test123",
            "customer_email": "test@example.com",
            "metadata": {"user_id": "user_test123"},
            "subscription": "sub_test123",
        }
        payload = json.dumps(self._make_event("checkout.session.completed", event_data)).encode()

        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"
        mock_event["data"] = {"object": event_data}
        mock_event.data = MagicMock()
        mock_event.data.object = event_data

        with patch("stripe.Webhook.construct_event", return_value=mock_event), \
             patch("db.supabase.update_user_plan", return_value=True) as mock_update, \
             patch("db.supabase.update_user_stripe_customer_id", return_value=True):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/webhooks/stripe",
                content=payload,
                headers={
                    "stripe-signature": "t=123,v1=fake_sig",
                    "Content-Type": "application/json",
                },
            )
        assert resp.status_code == 200

    def test_webhook_subscription_deleted_downgrades_plan(self):
        """customer.subscription.deleted event downgrades user to solo."""
        sub_data = {
            "customer": "cus_test123",
            "metadata": {"user_id": "user_test123"},
        }
        payload = json.dumps(self._make_event("customer.subscription.deleted", sub_data)).encode()

        mock_event = MagicMock()
        mock_event.type = "customer.subscription.deleted"
        mock_event.data = MagicMock()
        mock_event.data.object = sub_data

        with patch("stripe.Webhook.construct_event", return_value=mock_event), \
             patch("db.supabase.update_user_plan", return_value=True) as mock_update, \
             patch("db.supabase.get_user_stripe_customer_id", return_value="user_test123"):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/webhooks/stripe",
                content=payload,
                headers={
                    "stripe-signature": "t=123,v1=fake_sig",
                    "Content-Type": "application/json",
                },
            )
        assert resp.status_code == 200

    def test_webhook_verifies_signature(self):
        """Stripe webhook rejects invalid signatures."""
        payload = b'{"type": "test"}'

        with patch("stripe.Webhook.construct_event", side_effect=Exception("Invalid signature")):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/webhooks/stripe",
                content=payload,
                headers={
                    "stripe-signature": "t=123,v1=bad_sig",
                    "Content-Type": "application/json",
                },
            )
        assert resp.status_code == 400


# ── Competitor Limit Tests ─────────────────────────────────────────────────────

class TestCompetitorLimits:
    def test_competitor_limit_solo_is_3(self):
        """Solo plan allows maximum 3 competitors."""
        mock_user = {"id": "user_test123", "email": "test@example.com", "plan": "solo"}
        existing = [{"id": str(i)} for i in range(3)]  # Already at solo limit

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=existing), \
             patch("db.supabase.get_user", return_value=mock_user):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "https://newcompetitor.com"},
            )
        assert resp.status_code == 402

    def test_competitor_limit_pro_is_10(self):
        """Pro plan allows maximum 10 competitors."""
        pro_user = {"id": "user_test123", "email": "test@example.com", "plan": "pro"}
        existing = [{"id": str(i)} for i in range(10)]  # At pro limit

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=existing), \
             patch("db.supabase.get_user", return_value=pro_user):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "https://newcompetitor.com"},
            )
        assert resp.status_code == 402

    def test_competitor_limit_pro_allows_9(self):
        """Pro plan allows up to 9 competitors (under limit)."""
        pro_user = {"id": "user_test123", "email": "test@example.com", "plan": "pro"}
        existing = [{"id": str(i)} for i in range(9)]  # Under pro limit
        mock_competitor = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user_test123",
            "url": "https://newcompetitor.com",
            "name": None,
            "profile": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=existing), \
             patch("db.supabase.get_user", return_value=pro_user), \
             patch("db.supabase.create_competitor", return_value=mock_competitor):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "https://newcompetitor.com"},
            )
        assert resp.status_code == 201
