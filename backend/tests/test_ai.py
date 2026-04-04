"""
Tests for AI digest generation service (OpenRouter/Kimi K2.5 version).
Updated for cost-optimized implementation with caching.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Env vars
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-pem-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")


# ── Fixtures ───────────────────────────────────────────────────────────────────

MOCK_SCRAPED_DATA = {
    "url": "https://acme.com",
    "title": "Acme Corp - Project Management Software",
    "description": "Simple project management for teams.",
    "pricing": ["$29/mo Basic", "$99/mo Pro"],
    "features": ["Task tracking", "Gantt charts", "Team collaboration"],
    "headings": ["Features", "Pricing", "Contact"],
    "ctas": ["Start Free Trial", "View Pricing"],
}

MOCK_DIFF_RESULT = {
    "has_changes": True,
    "changes": [
        {
            "field": "pricing",
            "type": "added",
            "old_value": None,
            "new_value": "$149/mo Enterprise",
            "significance": "high",
        },
        {
            "field": "features",
            "type": "added",
            "old_value": None,
            "new_value": "AI-powered insights",
            "significance": "medium",
        },
    ],
    "significance_summary": "high",
}

MOCK_COMPETITORS_WITH_DIFFS = [
    {
        "competitor_name": "Acme Corp",
        "url": "https://acme.com",
        "diff_result": MOCK_DIFF_RESULT,
        "current_profile": "## Acme Corp\n**Pricing:** $29/mo Basic",
    },
    {
        "competitor_name": "Widget Co",
        "url": "https://widget.co",
        "diff_result": {"has_changes": False, "changes": [], "significance_summary": "none"},
        "current_profile": "## Widget Co\n**Pricing:** $49/mo",
    },
]

MOCK_PROFILE_RESPONSE = """## Acme Corp
**Pricing:** $29/mo Basic, $99/mo Pro
**Key features:** Task tracking, Gantt charts, Team collaboration
**Positioning:** Simple project management for teams."""

MOCK_DIGEST_RESPONSE = """<!-- SUBJECT: Your RivalEdge Weekly Brief — 1 change detected -->
<!DOCTYPE html>
<html>
<body>
<h1>Your RivalEdge Weekly Brief</h1>
<h2>Acme Corp</h2>
<p>New Enterprise tier at $149/mo — they're moving upmarket.</p>
<h2>No Changes</h2>
<p>Widget Co: No changes detected this week.</p>
</body>
</html>"""

MOCK_BATTLE_CARD_RESPONSE = """# How to Beat Acme Corp
## Their Weaknesses
- Complex onboarding
## Our Advantages
- Better pricing
## Objection Handling
- If they say Acme: point to our AI features
## Pricing Comparison
| Product | Price |
|---------|-------|
| Acme Corp | $29/mo |
| RivalEdge | $49/mo Solo |"""


def _make_mock_openrouter_response(response_text: str):
    """Create a mock httpx response that returns the given text."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": response_text}}]
    }
    mock_response.raise_for_status = MagicMock()
    return mock_response


# ── Tests: generate_competitor_profile ────────────────────────────────────────

class TestGenerateCompetitorProfile:
    def test_generate_profile_returns_markdown(self):
        """generate_competitor_profile returns markdown with ## header."""
        from services.ai import generate_competitor_profile, clear_ai_cache
        
        clear_ai_cache()  # Ensure no cache hit
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_PROFILE_RESPONSE)
            result = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert isinstance(result, str)
        assert result.startswith("##")
        assert "Acme Corp" in result

    def test_generate_profile_includes_pricing_section(self):
        """Profile contains a Pricing line."""
        from services.ai import generate_competitor_profile, clear_ai_cache
        
        clear_ai_cache()
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_PROFILE_RESPONSE)
            result = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert "**Pricing:**" in result

    def test_generate_profile_includes_features_section(self):
        """Profile contains a Key features line."""
        from services.ai import generate_competitor_profile, clear_ai_cache
        
        clear_ai_cache()
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_PROFILE_RESPONSE)
            result = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert "**Key features:**" in result

    def test_generate_profile_uses_cache(self):
        """Profile generation caches results."""
        from services.ai import generate_competitor_profile, clear_ai_cache, get_cache_stats
        
        clear_ai_cache()
        
        # First call — should hit API
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_PROFILE_RESPONSE)
            result1 = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        # Second call with same data — should hit cache
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response("WRONG RESPONSE")
            result2 = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        # Results should be identical (from cache)
        assert result1 == result2
        assert get_cache_stats()["size"] >= 1


# ── Tests: generate_weekly_digest ─────────────────────────────────────────────

class TestGenerateWeeklyDigest:
    def test_generate_digest_includes_all_competitors(self):
        """Digest HTML references all competitors by name."""
        from services.ai import generate_weekly_digest
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_DIGEST_RESPONSE)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        assert isinstance(result, str)
        assert "Acme Corp" in result
        assert "Widget Co" in result

    def test_generate_digest_returns_html(self):
        """Digest output is HTML."""
        from services.ai import generate_weekly_digest
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_DIGEST_RESPONSE)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        assert "<" in result  # Has HTML tags

    def test_generate_digest_has_subject_line(self):
        """Digest starts with <!-- SUBJECT: ... --> comment."""
        from services.ai import generate_weekly_digest
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_DIGEST_RESPONSE)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        assert result.startswith("<!-- SUBJECT:")

    def test_generate_digest_not_cached(self):
        """Digests are not cached (personalized per user)."""
        from services.ai import generate_weekly_digest, clear_ai_cache, get_cache_stats
        
        clear_ai_cache()
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_DIGEST_RESPONSE)
            generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        # Digest should not be cached
        assert get_cache_stats()["size"] == 0


# ── Tests: generate_battle_card ───────────────────────────────────────────────

class TestGenerateBattleCard:
    def test_generate_battle_card_returns_markdown(self):
        """generate_battle_card returns markdown with # header."""
        from services.ai import generate_battle_card, clear_ai_cache
        
        clear_ai_cache()
        
        our_product = {
            "name": "RivalEdge",
            "pricing": "$49/mo Solo, $99/mo Pro",
            "features": ["AI digests", "Weekly briefings", "Battle cards"],
        }
        competitor_profile = {
            "name": "Acme Corp",
            "pricing": "$29/mo",
            "features": ["Task tracking"],
        }
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_BATTLE_CARD_RESPONSE)
            result = generate_battle_card("Acme Corp", competitor_profile, our_product)
        
        assert isinstance(result, str)
        assert "# How to Beat" in result
        assert "Acme Corp" in result

    def test_generate_battle_card_includes_required_sections(self):
        """Battle card contains all 4 required sections."""
        from services.ai import generate_battle_card, clear_ai_cache
        
        clear_ai_cache()
        
        our_product = {
            "name": "RivalEdge",
            "pricing": "$49/mo Solo",
            "features": ["AI digests"],
        }
        competitor_profile = {"name": "Acme", "pricing": "$29/mo", "features": []}
        
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_BATTLE_CARD_RESPONSE)
            result = generate_battle_card("Acme", competitor_profile, our_product)
        
        assert "## Their Weaknesses" in result
        assert "## Our Advantages" in result
        assert "## Objection Handling" in result
        assert "## Pricing Comparison" in result

    def test_generate_battle_card_uses_cache(self):
        """Battle cards are cached for same competitor/product combo."""
        from services.ai import generate_battle_card, clear_ai_cache
        
        clear_ai_cache()
        
        our_product = {"name": "RivalEdge", "pricing": "$49", "features": []}
        competitor_profile = {"name": "Acme", "pricing": "$29", "features": []}
        
        # First call
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_BATTLE_CARD_RESPONSE)
            result1 = generate_battle_card("Acme", competitor_profile, our_product)
        
        # Second call — should hit cache
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response("WRONG")
            result2 = generate_battle_card("Acme", competitor_profile, our_product)
        
        assert result1 == result2


# ── Tests: Cache Management ───────────────────────────────────────────────────

class TestCacheManagement:
    def test_clear_cache_removes_all_entries(self):
        """clear_ai_cache removes all cached entries."""
        from services.ai import (
            generate_competitor_profile,
            clear_ai_cache,
            get_cache_stats,
        )
        
        clear_ai_cache()
        
        # Add something to cache
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _make_mock_openrouter_response(MOCK_PROFILE_RESPONSE)
            generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert get_cache_stats()["size"] >= 1
        
        # Clear cache
        clear_ai_cache()
        
        assert get_cache_stats()["size"] == 0

    def test_cache_stats_returns_valid_data(self):
        """get_cache_stats returns cache statistics."""
        from services.ai import get_cache_stats, clear_ai_cache
        
        clear_ai_cache()
        stats = get_cache_stats()
        
        assert "size" in stats
        assert "directory" in stats
        assert isinstance(stats["size"], int)
