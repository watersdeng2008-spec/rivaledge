"""
Tests for competitor endpoints.
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

MOCK_COMPETITOR = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_test123",
    "url": "https://competitor.com",
    "name": "Competitor Inc",
    "profile": None,
    "created_at": "2024-01-01T00:00:00+00:00",
}


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestListCompetitors:
    def test_returns_empty_list_for_new_user(self):
        """GET /api/competitors/ returns empty list for user with no competitors."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=[]):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["competitors"] == []
        assert data["total"] == 0

    def test_returns_list_of_competitors(self):
        """GET /api/competitors/ returns user's tracked competitors."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=[MOCK_COMPETITOR]):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["competitors"][0]["url"] == "https://competitor.com"

    def test_requires_auth(self):
        """GET /api/competitors/ requires authentication."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/competitors/")
        assert resp.status_code in (401, 403)  # FastAPI HTTPBearer returns 401 or 403


class TestAddCompetitor:
    def test_creates_competitor_successfully(self):
        """POST /api/competitors/ creates a new competitor."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=[]), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB), \
             patch("db.supabase.create_competitor", return_value=MOCK_COMPETITOR):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "https://competitor.com", "name": "Competitor Inc"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == "https://competitor.com"
        assert data["name"] == "Competitor Inc"

    def test_rejects_invalid_url(self):
        """POST /api/competitors/ rejects non-URL input."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "not-a-url"},
            )
        assert resp.status_code == 422  # Pydantic validation error

    def test_enforces_solo_plan_limit(self):
        """POST /api/competitors/ returns 402 when solo plan limit (3) is reached."""
        existing = [MOCK_COMPETITOR] * 3  # Already at limit
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=existing), \
             patch("db.supabase.get_user", return_value=MOCK_USER_DB):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "https://newcompetitor.com"},
            )
        assert resp.status_code == 402

    def test_pro_plan_allows_more_competitors(self):
        """POST /api/competitors/ allows up to 10 competitors on pro plan."""
        pro_user = {**MOCK_USER_DB, "plan": "pro"}
        existing = [MOCK_COMPETITOR] * 5  # Under pro limit (10)
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=existing), \
             patch("db.supabase.get_user", return_value=pro_user), \
             patch("db.supabase.create_competitor", return_value=MOCK_COMPETITOR):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/competitors/",
                headers={"Authorization": "Bearer fake-token"},
                json={"url": "https://competitor6.com"},
            )
        assert resp.status_code == 201


class TestRemoveCompetitor:
    def test_deletes_competitor(self):
        """DELETE /api/competitors/{id} removes a competitor."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.delete_competitor", return_value=True):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.delete(
                f"/api/competitors/550e8400-e29b-41d4-a716-446655440000",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 204

    def test_rejects_invalid_uuid(self):
        """DELETE /api/competitors/{id} rejects non-UUID path param."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.delete(
                "/api/competitors/not-a-uuid",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 422


class TestScraperDiff:
    def test_diff_detects_title_change(self):
        """diff_snapshots correctly identifies title changes."""
        from services.scraper import diff_snapshots
        
        old = {"title": "Old Title", "description": "Same desc", "text": "Same text"}
        new = {"title": "New Title", "description": "Same desc", "text": "Same text"}
        
        diff = diff_snapshots(old, new)
        
        assert "title" in diff
        assert diff["title"]["before"] == "Old Title"
        assert diff["title"]["after"] == "New Title"
        assert "description" not in diff
        assert "text" not in diff

    def test_diff_returns_empty_when_no_changes(self):
        """diff_snapshots returns empty dict when nothing changed."""
        from services.scraper import diff_snapshots
        
        snap = {"title": "Same", "description": "Same", "text": "Same"}
        diff = diff_snapshots(snap, snap)
        
        assert diff == {}

    def test_diff_handles_missing_fields(self):
        """diff_snapshots handles missing fields gracefully."""
        from services.scraper import diff_snapshots
        
        old = {}
        new = {"title": "New Title"}
        
        diff = diff_snapshots(old, new)
        
        assert "title" in diff
        assert diff["title"]["before"] == ""
        assert diff["title"]["after"] == "New Title"


class TestAuthModule:
    def test_verify_clerk_token_raises_on_invalid(self):
        """verify_clerk_token raises InvalidTokenError for garbage tokens."""
        import jwt as pyjwt
        from auth import verify_clerk_token
        
        # Temporarily set a valid-looking key
        os.environ["CLERK_PEM_PUBLIC_KEY"] = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBALRiMLAHudeSA/xKl1oGeUgaeOVFen6s\nXBnN4/TrPBLgBFdLTNFbLsxdqWsqWcfSW6H3k0iyEWnMSx3VmqSSdEkCAwEAAQ==\n-----END PUBLIC KEY-----"
        
        with pytest.raises(pyjwt.InvalidTokenError):
            verify_clerk_token("garbage.token.here")

    def test_get_current_user_dependency_rejects_no_header(self):
        """Endpoints using get_current_user return 401/403 with no auth header."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/users/me")
        assert resp.status_code in (401, 403)
