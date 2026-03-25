"""
Tests for Day 6 additions:
- GET /api/competitors/{id}/snapshots
- POST /api/digest/battle-card
"""
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-key")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

MOCK_USER = {
    "sub": "user_test123",
    "email": "test@example.com",
    "exp": 9999999999,
}

MOCK_COMPETITOR = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_test123",
    "url": "https://competitor.com",
    "name": "Competitor Inc",
    "profile": {"title": "Competitor homepage"},
    "created_at": "2024-01-01T00:00:00+00:00",
}

MOCK_SNAPSHOT = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "competitor_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": {"title": "Test page", "description": "A test description"},
    "diff": {"title": {"before": "Old", "after": "Test page"}},
    "created_at": "2024-01-07T12:00:00+00:00",
}


class TestGetSnapshots:
    def test_get_snapshots_returns_list(self):
        """GET /api/competitors/{id}/snapshots returns snapshots list."""
        snapshots = [MOCK_SNAPSHOT] * 3
        with patch("auth.verify_clerk_token", return_value=MOCK_USER), \
             patch("db.supabase.get_competitors", return_value=[MOCK_COMPETITOR]), \
             patch("db.supabase.get_competitor_snapshots", return_value=snapshots):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/competitors/550e8400-e29b-41d4-a716-446655440000/snapshots",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "snapshots" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["snapshots"]) == 3

    def test_get_snapshots_requires_auth(self):
        """GET /api/competitors/{id}/snapshots requires authentication."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get(
            "/api/competitors/550e8400-e29b-41d4-a716-446655440000/snapshots"
        )
        assert resp.status_code in (401, 403)

    def test_get_snapshots_limits_to_12(self):
        """GET /api/competitors/{id}/snapshots limits to last 12."""
        # The DB function is called with limit=12; verify it's called correctly
        snapshots = [MOCK_SNAPSHOT] * 12
        with patch("auth.verify_clerk_token", return_value=MOCK_USER), \
             patch("db.supabase.get_competitors", return_value=[MOCK_COMPETITOR]), \
             patch("db.supabase.get_competitor_snapshots", return_value=snapshots) as mock_fn:
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/competitors/550e8400-e29b-41d4-a716-446655440000/snapshots",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        # The mock was called with limit=12
        mock_fn.assert_called_once_with(
            "550e8400-e29b-41d4-a716-446655440000", limit=12
        )
        assert resp.json()["total"] == 12

    def test_get_snapshots_returns_404_for_wrong_competitor(self):
        """GET /api/competitors/{id}/snapshots returns 404 if competitor not owned by user."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER), \
             patch("db.supabase.get_competitors", return_value=[]):  # user has no competitors
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/competitors/550e8400-e29b-41d4-a716-446655440000/snapshots",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 404

    def test_snapshot_contains_expected_fields(self):
        """Each snapshot has id, created_at, diff, content_summary."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER), \
             patch("db.supabase.get_competitors", return_value=[MOCK_COMPETITOR]), \
             patch("db.supabase.get_competitor_snapshots", return_value=[MOCK_SNAPSHOT]):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/api/competitors/550e8400-e29b-41d4-a716-446655440000/snapshots",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        snap = resp.json()["snapshots"][0]
        assert "id" in snap
        assert "created_at" in snap
        assert "diff" in snap
        assert "content_summary" in snap


class TestBattleCard:
    def test_battle_card_endpoint_returns_markdown(self):
        """POST /api/digest/battle-card returns markdown battle card."""
        mock_battle_card = "# How to Beat Competitor Inc\n\n## Key Weaknesses\n- Expensive"
        with patch("auth.verify_clerk_token", return_value=MOCK_USER), \
             patch("db.supabase.get_competitors", return_value=[MOCK_COMPETITOR]), \
             patch("services.ai.generate_battle_card", return_value=mock_battle_card):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/digest/battle-card",
                headers={"Authorization": "Bearer fake-token"},
                json={"competitor_id": "550e8400-e29b-41d4-a716-446655440000"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "battle_card" in data
        assert "Beat" in data["battle_card"] or "#" in data["battle_card"]

    def test_battle_card_requires_auth(self):
        """POST /api/digest/battle-card requires authentication."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/digest/battle-card",
            json={"competitor_id": "550e8400-e29b-41d4-a716-446655440000"},
        )
        assert resp.status_code in (401, 403)

    def test_battle_card_returns_404_for_unknown_competitor(self):
        """POST /api/digest/battle-card returns 404 if competitor not found."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER), \
             patch("db.supabase.get_competitors", return_value=[]):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/digest/battle-card",
                headers={"Authorization": "Bearer fake-token"},
                json={"competitor_id": "nonexistent-id"},
            )
        assert resp.status_code == 404

    def test_battle_card_requires_competitor_id(self):
        """POST /api/digest/battle-card returns 400 if competitor_id missing."""
        with patch("auth.verify_clerk_token", return_value=MOCK_USER):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/digest/battle-card",
                headers={"Authorization": "Bearer fake-token"},
                json={},
            )
        assert resp.status_code == 400
