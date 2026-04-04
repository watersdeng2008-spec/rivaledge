"""
AI service — generates competitor intelligence using OpenRouter (Kimi K2.5 default).

Cost-optimized implementation:
- Kimi K2.5 for all tasks (80-90% cheaper than Claude Sonnet 4.6)
- Disk-based caching to avoid redundant AI calls
- Token-efficient prompts
"""
import os
import logging
import hashlib
from typing import Optional
from pathlib import Path

import httpx
from diskcache import Cache

logger = logging.getLogger(__name__)

# Configuration
AI_MODEL = os.environ.get("AI_MODEL", "moonshotai/kimi-k2.5")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Cache setup — persists across restarts
CACHE_DIR = Path(__file__).parent / ".ai_cache"
cache = Cache(str(CACHE_DIR))


def _get_cache_key(prefix: str, content: str) -> str:
    """Generate deterministic cache key from content."""
    hash_input = f"{prefix}:{content}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:32]


def _call_ai(system: str, user: str, max_tokens: int = 4000, use_cache: bool = True) -> str:
    """
    Call AI via OpenRouter with caching support.
    
    Args:
        system: System prompt
        user: User prompt  
        max_tokens: Max tokens to generate
        use_cache: Whether to check/save cache
        
    Returns:
        Generated text
    """
    # Check cache first
    cache_key = _get_cache_key("ai", f"{system}:{user}:{max_tokens}")
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"AI cache hit: {cache_key[:8]}...")
            return cached
    
    # Call OpenRouter
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://rivaledge.ai",
        "X-Title": "RivalEdge",
    }
    
    payload = {
        "model": AI_MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    
    try:
        response = httpx.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()
        
        result = data["choices"][0]["message"]["content"]
        
        # Cache the result
        if use_cache:
            cache.set(cache_key, result, expire=86400 * 7)  # 7 days
            logger.info(f"AI cache saved: {cache_key[:8]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        raise


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
    Cached to avoid re-analyzing the same content.
    """
    # Build compact summary
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
    
    return _call_ai(
        system=PROFILE_SYSTEM,
        user=f"Generate a competitor profile from this scraped data:\n\n{scraped_summary}",
        max_tokens=2000,
        use_cache=True,
    )


# ── Weekly Digest ──────────────────────────────────────────────────────────────

DIGEST_SYSTEM = """You are a competitive intelligence analyst for RivalEdge. Generate a mobile-friendly HTML email digest.

Requirements:
1. First line must be: <!-- SUBJECT: [subject line] -->
2. Use inline CSS, max-width 600px, dark background (#0f172a), white text, mobile-responsive
3. Header: "Your RivalEdge Weekly Brief"
4. ALWAYS include a "Competitor Snapshot" section for ALL competitors with:
   - Competitor name + URL as a section header
   - Current pricing (if known)
   - Top 3 features or value propositions
   - Their main positioning/tagline
5. For competitors WITH changes (has_changes=True): also show what changed this week
6. For competitors with NO changes: show the snapshot with a note "No changes detected this week"
7. Footer with: {{unsubscribe_url}} placeholder
8. Keep tone sharp and actionable — like a briefing from a sharp analyst
9. End with a "What to watch" section: 1-2 strategic observations about the competitive landscape"""


def generate_weekly_digest(user_email: str, competitors_with_diffs: list[dict]) -> str:
    """
    Generate a full HTML email digest for the user.
    Cached per user per week based on competitor data hash.
    """
    # Build context
    changed = [c for c in competitors_with_diffs if c.get("diff_result", {}).get("has_changes")]
    unchanged = [c for c in competitors_with_diffs if not c.get("diff_result", {}).get("has_changes")]
    
    change_count = len(changed)
    high_sig_count = sum(
        1 for c in changed
        if c.get("diff_result", {}).get("significance_summary") == "high"
    )
    
    # Format changed competitors
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
        
        for ch in other_changes[:5]:
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
    
    return _call_ai(
        system=DIGEST_SYSTEM,
        user=prompt,
        max_tokens=4000,
        use_cache=False,  # Digests are personalized per user
    )


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
    Cached to avoid regenerating for same competitor/product combo.
    """
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
    
    return _call_ai(
        system=BATTLE_CARD_SYSTEM,
        user=prompt,
        max_tokens=2000,
        use_cache=True,
    )


# ── Cache Management ───────────────────────────────────────────────────────────

def clear_ai_cache():
    """Clear all cached AI responses."""
    cache.clear()
    logger.info("AI cache cleared")


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "size": len(cache),
        "directory": str(CACHE_DIR),
    }
