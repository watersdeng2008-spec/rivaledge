"""
Tests for scraper, differ, and jobs endpoints.
Written FIRST (TDD) — then implementation follows.
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Env vars
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-pem-key")
os.environ.setdefault("BRAVE_SEARCH_API_KEY", "test-brave-key")

from fastapi.testclient import TestClient

MOCK_USER_PAYLOAD = {
    "sub": "user_test123",
    "email": "test@example.com",
    "exp": 9999999999,
}

MOCK_COMPETITOR = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_test123",
    "url": "https://example.com",
    "name": "Example Co",
    "profile": None,
    "created_at": "2024-01-01T00:00:00+00:00",
}

MOCK_SNAPSHOT_CONTENT = {
    "url": "https://example.com",
    "scraped_at": "2024-01-01T00:00:00+00:00",
    "title": "Example Company",
    "description": "The best example company",
    "pricing": ["$29/mo", "$99/month"],
    "features": ["Feature A", "Feature B"],
    "headings": ["Welcome to Example", "Why Choose Us"],
    "ctas": ["Sign up free", "Get started"],
    "raw_text": "Welcome to Example Company. Sign up free today.",
    "source": "playwright",
}

MOCK_SNAPSHOT_DB = {
    "id": "aaa-bbb-ccc",
    "competitor_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": MOCK_SNAPSHOT_CONTENT,
    "diff": None,
    "created_at": "2024-01-01T00:00:00+00:00",
}


# ── Test: Scraper Structure ────────────────────────────────────────────────────

class TestScraperReturnsExpectedStructure:
    @pytest.mark.asyncio
    async def test_scraper_returns_expected_structure(self):
        """scrape_url returns all required fields."""
        from services.scraper import scrape_url

        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Title")
        mock_page.evaluate = AsyncMock(side_effect=lambda expr: {
            "document.querySelector('meta[name=description]')?.content || ''": "Test desc",
            "document.body?.innerText || ''": "Some page text " * 100,
        }.get(expr, []))
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.goto = AsyncMock()
        mock_page.set_extra_http_headers = AsyncMock()
        mock_page.route = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_chromium = MagicMock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw = AsyncMock()
        mock_pw.chromium = mock_chromium
        mock_pw.__aenter__ = AsyncMock(return_value=mock_pw)
        mock_pw.__aexit__ = AsyncMock(return_value=None)

        with patch("playwright.async_api.async_playwright", return_value=mock_pw):
            result = await scrape_url("https://example.com")

        assert isinstance(result, dict)
        required_fields = ["url", "scraped_at", "title", "description", "pricing",
                           "features", "headings", "ctas", "raw_text", "source"]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        assert result["url"] == "https://example.com"
        assert isinstance(result["pricing"], list)
        assert isinstance(result["features"], list)
        assert isinstance(result["headings"], list)
        assert isinstance(result["ctas"], list)
        assert isinstance(result["raw_text"], str)
        assert len(result["raw_text"]) <= 5000
        assert result["source"] in ("playwright", "brave_fallback")


class TestScraperHandlesInvalidUrl:
    @pytest.mark.asyncio
    async def test_scraper_handles_invalid_url(self):
        """scrape_url falls back to Brave when Playwright fails."""
        from services.scraper import scrape_url

        # Playwright raises an exception
        mock_pw = AsyncMock()
        mock_pw.__aenter__ = AsyncMock(side_effect=Exception("Connection failed"))
        mock_pw.__aexit__ = AsyncMock(return_value=None)

        brave_response = MagicMock()
        brave_response.raise_for_status = MagicMock()
        brave_response.json = MagicMock(return_value={
            "web": {"results": [{"title": "Fallback", "description": "Brave fallback content"}]}
        })

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=brave_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("playwright.async_api.async_playwright", return_value=mock_pw), \
             patch("httpx.AsyncClient", return_value=mock_client):
            result = await scrape_url("not-a-real-url")

        assert result["source"] == "brave_fallback"
        assert "title" in result


class TestScraperTimeoutFallback:
    @pytest.mark.asyncio
    async def test_scraper_timeout_falls_back_to_brave(self):
        """When Playwright times out, falls back to Brave Search."""
        from services.scraper import scrape_url

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Timeout 30000ms exceeded"))
        mock_page.set_extra_http_headers = AsyncMock()
        mock_page.route = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_chromium = MagicMock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw = AsyncMock()
        mock_pw.chromium = mock_chromium
        mock_pw.__aenter__ = AsyncMock(return_value=mock_pw)
        mock_pw.__aexit__ = AsyncMock(return_value=None)

        brave_response = MagicMock()
        brave_response.raise_for_status = MagicMock()
        brave_response.json = MagicMock(return_value={
            "web": {"results": [{"title": "Fallback Title", "description": "Fallback from Brave"}]}
        })

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=brave_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)

        with patch("playwright.async_api.async_playwright", return_value=mock_pw), \
             patch("httpx.AsyncClient", return_value=mock_http_client):
            result = await scrape_url("https://slow-site.com")

        assert result["source"] == "brave_fallback"


# ── Test: Differ ───────────────────────────────────────────────────────────────

class TestDiffDetectsPricingChange:
    def test_diff_detects_pricing_change(self):
        """diff_snapshots detects pricing changes."""
        from services.differ import diff_snapshots

        old = {**MOCK_SNAPSHOT_CONTENT, "pricing": ["$29/mo"]}
        new = {**MOCK_SNAPSHOT_CONTENT, "pricing": ["$49/mo"]}

        result = diff_snapshots(old, new)

        assert result["has_changes"] is True
        pricing_changes = [c for c in result["changes"] if c["field"] == "pricing"]
        assert len(pricing_changes) > 0


class TestDiffDetectsNoChanges:
    def test_diff_detects_no_changes(self):
        """diff_snapshots returns has_changes=False when nothing changed."""
        from services.differ import diff_snapshots

        result = diff_snapshots(MOCK_SNAPSHOT_CONTENT, MOCK_SNAPSHOT_CONTENT)

        assert result["has_changes"] is False
        assert result["changes"] == []
        assert isinstance(result["summary"], str)


class TestDiffSignificancePricingIsHigh:
    def test_diff_significance_pricing_is_high(self):
        """Pricing changes have high significance."""
        from services.differ import diff_snapshots

        old = {**MOCK_SNAPSHOT_CONTENT, "pricing": ["$29/mo"]}
        new = {**MOCK_SNAPSHOT_CONTENT, "pricing": ["$49/mo"]}

        result = diff_snapshots(old, new)

        pricing_changes = [c for c in result["changes"] if c["field"] == "pricing"]
        assert len(pricing_changes) > 0
        assert pricing_changes[0]["significance"] == "high"

    def test_diff_significance_title_is_high(self):
        """Title changes have high significance."""
        from services.differ import diff_snapshots

        old = {**MOCK_SNAPSHOT_CONTENT, "title": "Old Title"}
        new = {**MOCK_SNAPSHOT_CONTENT, "title": "New Title"}

        result = diff_snapshots(old, new)

        title_changes = [c for c in result["changes"] if c["field"] == "title"]
        assert len(title_changes) > 0
        assert title_changes[0]["significance"] == "high"

    def test_diff_significance_features_is_medium(self):
        """Feature changes have medium significance."""
        from services.differ import diff_snapshots

        old = {**MOCK_SNAPSHOT_CONTENT, "features": ["Feature A"]}
        new = {**MOCK_SNAPSHOT_CONTENT, "features": ["Feature A", "Feature B"]}

        result = diff_snapshots(old, new)

        feature_changes = [c for c in result["changes"] if c["field"] == "features"]
        assert len(feature_changes) > 0
        assert feature_changes[0]["significance"] == "medium"

    def test_diff_significance_description_is_low(self):
        """Description changes have low significance."""
        from services.differ import diff_snapshots

        old = {**MOCK_SNAPSHOT_CONTENT, "description": "Old description"}
        new = {**MOCK_SNAPSHOT_CONTENT, "description": "New description"}

        result = diff_snapshots(old, new)

        desc_changes = [c for c in result["changes"] if c["field"] == "description"]
        assert len(desc_changes) > 0
        assert desc_changes[0]["significance"] == "low"


# ── Test: Jobs Endpoint Requires Auth ─────────────────────────────────────────

class TestJobsEndpointRequiresAuth:
    def test_scrape_single_requires_auth(self):
        """POST /api/jobs/scrape/{id} requires authentication."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/jobs/scrape/550e8400-e29b-41d4-a716-446655440000")
        assert resp.status_code in (401, 403)

    def test_scrape_all_requires_auth(self):
        """POST /api/jobs/scrape-all requires authentication."""
        from main import app
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/jobs/scrape-all")
        assert resp.status_code in (401, 403)

    def test_scrape_single_with_valid_auth(self):
        """POST /api/jobs/scrape/{id} works with valid auth."""
        mock_snapshot_content = MOCK_SNAPSHOT_CONTENT.copy()

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_client"), \
             patch("routers.jobs.get_competitor_for_user", return_value=MOCK_COMPETITOR), \
             patch("routers.jobs.scrape_url", return_value=mock_snapshot_content), \
             patch("routers.jobs.get_latest_snapshot", return_value=None), \
             patch("routers.jobs.save_snapshot", return_value={**MOCK_SNAPSHOT_DB, "id": "new-snap-id"}):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/jobs/scrape/550e8400-e29b-41d4-a716-446655440000",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "snapshot_id" in data
        assert "changes" in data

    def test_scrape_all_with_valid_auth(self):
        """POST /api/jobs/scrape-all works with valid auth."""
        mock_snapshot_content = MOCK_SNAPSHOT_CONTENT.copy()

        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_client"), \
             patch("routers.jobs.get_user_competitors", return_value=[MOCK_COMPETITOR]), \
             patch("routers.jobs.scrape_url", return_value=mock_snapshot_content), \
             patch("routers.jobs.get_latest_snapshot", return_value=None), \
             patch("routers.jobs.save_snapshot", return_value={**MOCK_SNAPSHOT_DB, "id": "new-snap-id"}):
            from main import app
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/jobs/scrape-all",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "scraped" in data
        assert "failed" in data
        assert "results" in data
