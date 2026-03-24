"""
AI service — generates competitor intelligence using Anthropic Claude.

Day 3: Full implementation of generate_competitor_profile, 
generate_weekly_digest, and generate_battle_card.
"""
import os
import logging
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-3-5-sonnet-20241022"


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)


# ── Competitor Profile ─────────────────────────────────────────────────────────

PROFILE_SYSTEM = """You are a competitive intelligence analyst. Given raw scraped data from a competitor's website, produce a concise markdown profile.

Output ONLY this format (no extra commentary):
## [Competitor Name]
**Pricing:** [price tiers, e.g. $49/mo Solo, $99/mo Pro — or "Not listed" if absent]
**Key features:** [Feature 1, Feature 2, Feature 3 — comma separated, max 5]
**Positioning:** [1 sentence tagline or positioning statement]"""


def generate_competitor_profile(scraped_data: dict) -> str:
    """
    Takes raw scraper output, returns a clean markdown competitor profile.
    
    Args:
        scraped_data: Dict with keys: url, title, description, pricing, features, etc.
    
    Returns:
        Markdown-formatted profile string.
    """
    client = _get_client()
    
    # Build a compact summary of scraped data for the prompt
    parts = []
    if scraped_data.get("url"):
        parts.append(f"URL: {scraped_data['url']}")
    if scraped_data.get("title"):
        parts.append(f"Page Title: {scraped_data['title']}")
    if scraped_data.get("description"):
        parts.append(f"Description: {scraped_data['description']}")
    if scraped_data.get("pricing"):
        pricing = scraped_data["pricing"]
        if isinstance(pricing, list):
            parts.append(f"Pricing mentions: {', '.join(str(p) for p in pricing[:10])}")
        else:
            parts.append(f"Pricing: {pricing}")
    if scraped_data.get("features"):
        features = scraped_data["features"]
        if isinstance(features, list):
            parts.append(f"Features: {', '.join(str(f) for f in features[:10])}")
        else:
            parts.append(f"Features: {features}")
    if scraped_data.get("ctas"):
        ctas = scraped_data["ctas"]
        if isinstance(ctas, list):
            parts.append(f"CTAs: {', '.join(str(c) for c in ctas[:5])}")
    
    scraped_summary = "\n".join(parts)
    
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=PROFILE_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Generate a competitor profile from this scraped data:\n\n{scraped_summary}",
            }
        ],
    )
    
    return message.content[0].text


# ── Weekly Digest ──────────────────────────────────────────────────────────────

DIGEST_SYSTEM = """You are a competitive intelligence analyst for RivalEdge. Generate a mobile-friendly HTML email digest summarizing competitor changes for the week.

Requirements:
1. First line must be: <!-- SUBJECT: [subject line] -->
2. Use inline CSS, max-width 600px, mobile-responsive
3. Header: "Your RivalEdge Weekly Brief"
4. For competitors WITH changes (has_changes=True):
   - Show competitor name + URL as a section header
   - Bullet list of what changed (pricing, features, etc.)
   - "What this means" — 1-2 sentence strategic interpretation
   - Emphasize HIGH significance changes prominently
5. For competitors with NO changes: group them in a brief "No changes detected" section
6. Footer with: {{unsubscribe_url}} placeholder for unsubscribe link
7. Keep tone professional but concise"""


def generate_weekly_digest(user_email: str, competitors_with_diffs: list[dict]) -> str:
    """
    Generate a full HTML email digest for the user.
    
    Args:
        user_email: The user's email address (for personalization)
        competitors_with_diffs: List of dicts with keys:
            - competitor_name: str
            - url: str
            - diff_result: dict (has_changes, changes, significance_summary)
            - current_profile: str (markdown profile)
    
    Returns:
        Full HTML email body string, starting with <!-- SUBJECT: ... -->
    """
    client = _get_client()
    
    # Build context for Claude
    changed = [c for c in competitors_with_diffs if c.get("diff_result", {}).get("has_changes")]
    unchanged = [c for c in competitors_with_diffs if not c.get("diff_result", {}).get("has_changes")]
    
    change_count = len(changed)
    high_sig_count = sum(
        1 for c in changed
        if c.get("diff_result", {}).get("significance_summary") == "high"
    )
    
    # Format changed competitors for the prompt
    changed_sections = []
    for comp in changed:
        diff = comp.get("diff_result", {})
        changes = diff.get("changes", [])
        sig = diff.get("significance_summary", "low")
        
        high_changes = [ch for ch in changes if ch.get("significance") == "high"]
        other_changes = [ch for ch in changes if ch.get("significance") != "high"]
        
        change_bullets = []
        for ch in high_changes:
            field = ch.get("field", "")
            change_type = ch.get("type", "changed")
            new_val = ch.get("new_value", "")
            old_val = ch.get("old_value", "")
            if change_type == "added":
                change_bullets.append(f"[HIGH] {field.upper()} ADDED: {new_val}")
            elif change_type == "removed":
                change_bullets.append(f"[HIGH] {field.upper()} REMOVED: {old_val}")
            else:
                change_bullets.append(f"[HIGH] {field.upper()} CHANGED: {old_val} → {new_val}")
        
        for ch in other_changes[:5]:  # limit to 5 other changes
            field = ch.get("field", "")
            change_type = ch.get("type", "changed")
            new_val = ch.get("new_value", "")
            old_val = ch.get("old_value", "")
            sig_label = ch.get("significance", "low").upper()
            if change_type == "added":
                change_bullets.append(f"[{sig_label}] {field}: added '{new_val}'")
            elif change_type == "removed":
                change_bullets.append(f"[{sig_label}] {field}: removed '{old_val}'")
            else:
                change_bullets.append(f"[{sig_label}] {field}: '{old_val}' → '{new_val}'")
        
        changes_text = "\n".join(f"  • {b}" for b in change_bullets) if change_bullets else "  • General content updates"
        
        changed_sections.append(
            f"COMPETITOR: {comp['competitor_name']}\n"
            f"URL: {comp['url']}\n"
            f"Overall significance: {sig}\n"
            f"Changes:\n{changes_text}"
        )
    
    unchanged_names = [c["competitor_name"] for c in unchanged]
    
    prompt = f"""Generate a weekly competitor digest email for {user_email}.

Summary: {change_count} competitor(s) with changes, {high_sig_count} high-significance.

COMPETITORS WITH CHANGES:
{chr(10).join(changed_sections) if changed_sections else "None this week."}

COMPETITORS WITH NO CHANGES:
{', '.join(unchanged_names) if unchanged_names else "None"}

Generate a complete HTML email following the system instructions."""
    
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4000,
        system=DIGEST_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    
    return message.content[0].text


# ── Battle Card ────────────────────────────────────────────────────────────────

BATTLE_CARD_SYSTEM = """You are a sales enablement expert. Generate a battle card to help sales reps compete against a specific competitor.

Output ONLY markdown in this exact format:
# How to Beat [Competitor Name]

## Their Weaknesses
- [weakness 1]
- [weakness 2]
- [weakness 3]

## Our Advantages
- [advantage 1]
- [advantage 2]
- [advantage 3]

## Objection Handling
- **"They have [X]"**: [response]
- **"[Their price] is cheaper"**: [response]
- **"We already use them"**: [response]

## Pricing Comparison
| | [Competitor] | [Our Product] |
|---|---|---|
| Entry | [their entry price] | [our entry price] |
| Mid-tier | [their mid price] | [our mid price] |
| Top tier | [their top price] | [our top price] |"""


def generate_battle_card(
    competitor_name: str,
    competitor_profile: dict,
    our_product: dict,
) -> str:
    """
    Generate a sales battle card for a specific competitor.
    
    Args:
        competitor_name: Name of the competitor
        competitor_profile: Dict with competitor info (pricing, features, etc.)
        our_product: Dict with our product info:
            {name, pricing, features: list}
    
    Returns:
        Markdown-formatted battle card.
    """
    client = _get_client()
    
    our_name = our_product.get("name", "RivalEdge")
    our_pricing = our_product.get("pricing", "Contact for pricing")
    our_features = our_product.get("features", [])
    
    comp_pricing = competitor_profile.get("pricing", "Unknown")
    comp_features = competitor_profile.get("features", [])
    
    if isinstance(our_features, list):
        our_features_str = ", ".join(str(f) for f in our_features)
    else:
        our_features_str = str(our_features)
    
    if isinstance(comp_features, list):
        comp_features_str = ", ".join(str(f) for f in comp_features)
    else:
        comp_features_str = str(comp_features)
    
    prompt = f"""Generate a battle card comparing us vs {competitor_name}.

OUR PRODUCT: {our_name}
Our pricing: {our_pricing}
Our features: {our_features_str}

COMPETITOR: {competitor_name}
Their pricing: {comp_pricing}
Their features: {comp_features_str}"""
    
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=BATTLE_CARD_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    
    return message.content[0].text
