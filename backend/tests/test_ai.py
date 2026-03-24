"""
Tests for AI digest generation service.
Written FIRST (TDD) — all tests written before implementation.
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
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")


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

MOCK_CLAUDE_PROFILE_RESPONSE = """## Acme Corp
**Pricing:** $29/mo Basic, $99/mo Pro
**Key features:** Task tracking, Gantt charts, Team collaboration
**Positioning:** Simple project management for teams."""

MOCK_CLAUDE_DIGEST_RESPONSE = """<!-- SUBJECT: Your RivalEdge Weekly Brief — 1 change detected -->
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

MOCK_CLAUDE_BATTLE_CARD_RESPONSE = """# How to Beat Acme Corp
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


def _make_mock_anthropic(response_text: str):
    """Create a mock anthropic client that returns the given text."""
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    mock_client.messages.create.return_value = mock_message
    return mock_client


# ── Tests: generate_competitor_profile ────────────────────────────────────────

class TestGenerateCompetitorProfile:
    def test_generate_profile_returns_markdown(self):
        """generate_competitor_profile returns markdown with ## header."""
        from services.ai import generate_competitor_profile
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_PROFILE_RESPONSE)
            result = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert isinstance(result, str)
        assert result.startswith("##")
        assert "Acme Corp" in result

    def test_generate_profile_includes_pricing_section(self):
        """Profile contains a Pricing line."""
        from services.ai import generate_competitor_profile
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_PROFILE_RESPONSE)
            result = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert "**Pricing:**" in result

    def test_generate_profile_includes_features_section(self):
        """Profile contains a Key features line."""
        from services.ai import generate_competitor_profile
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_PROFILE_RESPONSE)
            result = generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        assert "**Key features:**" in result

    def test_generate_profile_calls_claude_with_max_tokens_2000(self):
        """Profile generation uses max_tokens=2000."""
        from services.ai import generate_competitor_profile
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_client = _make_mock_anthropic(MOCK_CLAUDE_PROFILE_RESPONSE)
            MockAnthropic.return_value = mock_client
            generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("max_tokens") == 2000

    def test_generate_profile_uses_correct_model(self):
        """Profile generation uses claude-3-5-sonnet-20241022."""
        from services.ai import generate_competitor_profile
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_client = _make_mock_anthropic(MOCK_CLAUDE_PROFILE_RESPONSE)
            MockAnthropic.return_value = mock_client
            generate_competitor_profile(MOCK_SCRAPED_DATA)
        
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("model") == "claude-3-5-sonnet-20241022"


# ── Tests: generate_weekly_digest ─────────────────────────────────────────────

class TestGenerateWeeklyDigest:
    def test_generate_digest_includes_all_competitors(self):
        """Digest HTML references all competitors by name."""
        from services.ai import generate_weekly_digest
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_DIGEST_RESPONSE)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        assert isinstance(result, str)
        assert "Acme Corp" in result
        assert "Widget Co" in result

    def test_generate_digest_highlights_high_significance_changes(self):
        """Digest emphasizes high-significance changes."""
        from services.ai import generate_weekly_digest
        
        # Response that explicitly mentions pricing change
        response_with_high_sig = MOCK_CLAUDE_DIGEST_RESPONSE.replace(
            "New Enterprise tier", "🚨 HIGH PRIORITY: New Enterprise tier"
        )
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(response_with_high_sig)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        # The prompt should include high-significance change info
        mock_client = MockAnthropic.return_value
        create_call = mock_client.messages.create.call_args
        prompt_content = str(create_call)
        # Verify high significance was passed to Claude
        assert "high" in prompt_content.lower() or "pricing" in prompt_content.lower()

    def test_generate_digest_returns_html(self):
        """Digest output is HTML."""
        from services.ai import generate_weekly_digest
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_DIGEST_RESPONSE)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        assert "<" in result  # Has HTML tags

    def test_generate_digest_has_subject_line(self):
        """Digest starts with <!-- SUBJECT: ... --> comment."""
        from services.ai import generate_weekly_digest
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_DIGEST_RESPONSE)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        assert result.startswith("<!-- SUBJECT:")

    def test_generate_digest_calls_claude_with_max_tokens_4000(self):
        """Digest generation uses max_tokens=4000."""
        from services.ai import generate_weekly_digest
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_client = _make_mock_anthropic(MOCK_CLAUDE_DIGEST_RESPONSE)
            MockAnthropic.return_value = mock_client
            generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("max_tokens") == 4000

    def test_generate_digest_includes_no_changes_section_when_applicable(self):
        """Digest mentions competitors with no changes."""
        from services.ai import generate_weekly_digest
        
        response_with_no_changes = MOCK_CLAUDE_DIGEST_RESPONSE
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(response_with_no_changes)
            result = generate_weekly_digest("user@example.com", MOCK_COMPETITORS_WITH_DIFFS)
        
        # Widget Co has no changes — should appear somewhere
        assert "Widget Co" in result


# ── Tests: generate_battle_card ───────────────────────────────────────────────

class TestGenerateBattleCard:
    def test_generate_battle_card_returns_markdown(self):
        """generate_battle_card returns markdown with # header."""
        from services.ai import generate_battle_card
        
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
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_BATTLE_CARD_RESPONSE)
            result = generate_battle_card("Acme Corp", competitor_profile, our_product)
        
        assert isinstance(result, str)
        assert "# How to Beat" in result
        assert "Acme Corp" in result

    def test_generate_battle_card_includes_required_sections(self):
        """Battle card contains all 4 required sections."""
        from services.ai import generate_battle_card
        
        our_product = {
            "name": "RivalEdge",
            "pricing": "$49/mo Solo",
            "features": ["AI digests"],
        }
        competitor_profile = {"name": "Acme", "pricing": "$29/mo", "features": []}
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value = _make_mock_anthropic(MOCK_CLAUDE_BATTLE_CARD_RESPONSE)
            result = generate_battle_card("Acme", competitor_profile, our_product)
        
        assert "## Their Weaknesses" in result
        assert "## Our Advantages" in result
        assert "## Objection Handling" in result
        assert "## Pricing Comparison" in result

    def test_generate_battle_card_uses_correct_model(self):
        """Battle card uses claude-3-5-sonnet-20241022."""
        from services.ai import generate_battle_card
        
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_client = _make_mock_anthropic(MOCK_CLAUDE_BATTLE_CARD_RESPONSE)
            MockAnthropic.return_value = mock_client
            generate_battle_card("Acme", {}, {"name": "RivalEdge", "pricing": "$49", "features": []})
        
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("model") == "claude-3-5-sonnet-20241022"
