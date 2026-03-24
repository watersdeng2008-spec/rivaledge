"""
Tests for user endpoints.
Written FIRST (TDD) — then implementation follows.
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Set required env vars before importing app
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-key")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Fixtures ───────────────────────────────────────────────────────────────────

MOCK_USER_PAYLOAD = {
    "sub": "user_test123",
    "email": "test@example.com",
    "exp": 9999999999,
}

MOCK_USER_DB = {
    "id": "user_test123",
    "email": "test@example.com",
    "plan": "solo",
    "created_at": "2024-01-01T00:00:00+00:00",
}


def get_mock_client():
    """Return a TestClient with auth mocked out."""
    with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD):
        from main import app
        return TestClient(app, raise_server_exceptions=False)


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestGetMe:
    def test_returns_user_profile_when_exists(self):
        """GET /api/users/me returns the user's profile."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/users/me",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "user_test123"
        assert data["email"] == "test@example.com"
        assert data["plan"] == "solo"

    def test_returns_404_when_user_not_in_db(self):
        """GET /api/users/me returns 404 if user hasn't been created yet."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_user", return_value=None):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/users/me",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 404

    def test_returns_401_without_auth_header(self):
        """GET /api/users/me requires authentication."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/users/me")
        assert resp.status_code in (401, 403)  # HTTPBearer returns 401 when no credentials

    def test_returns_401_with_invalid_token(self):
        """GET /api/users/me rejects invalid tokens."""
        import jwt as pyjwt
        with patch("auth.verify_clerk_token", side_effect=pyjwt.InvalidTokenError("bad")):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/users/me",
                headers={"Authorization": "Bearer invalid-token"},
            )
        assert resp.status_code == 401


class TestCreateMe:
    def test_upserts_user_on_post(self):
        """POST /api/users/me creates or updates user record."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.upsert_user", return_value=MOCK_USER_DB):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/users/me",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "user_test123"


class TestHealthCheck:
    def test_health_endpoint_returns_ok(self):
        """GET /health returns 200 with status ok."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
