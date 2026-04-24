"""
AI service — generates competitor intelligence using OpenRouter (Kimi K2.5 default).

Cost-optimized implementation:
- Kimi K2.5 for all tasks (80-90% cheaper than Claude Sonnet 4.6)
- Disk-based caching to avoid redundant AI calls
- Token-efficient prompts
- Comprehensive token usage tracking for cost optimization
"""
import os
import logging
import hashlib
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

import httpx
from diskcache import Cache

logger = logging.getLogger(__name__)

# Configuration
AI_MODEL = os.environ.get("AI_MODEL", "moonshotai/kimi-k2.5")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model selection by task
MODELS = {
    "default": os.environ.get("AI_MODEL", "moonshotai/kimi-k2.5"),
    "coding": os.environ.get("AI_MODEL_CODING", "moonshotai/kimi-k2.5"),
    "sales": os.environ.get("AI_MODEL_SALES", "qwen/qwen3.6-plus:free"),
    "marketing": os.environ.get("AI_MODEL_MARKETING", "qwen/qwen3.6-plus:free"),
    "research": os.environ.get("AI_MODEL_RESEARCH", "qwen/qwen3-30b-a3b:free"),
}

# Cache setup — persists across restarts
CACHE_DIR = Path(__file__).parent / ".ai_cache"
cache = Cache(str(CACHE_DIR))

# Token usage tracking
TOKEN_LOG_DIR = Path(__file__).parent / ".token_logs"
TOKEN_LOG_DIR.mkdir(exist_ok=True)

# Circuit breaker for autocompact failures (CSkill pattern)
CIRCUIT_BREAKER_THRESHOLD = 3
_circuit_breaker_state = {
    "consecutive_failures": 0,
    "tripped": False,
    "last_trip_time": None,
}

# Context budget management (CSkill pattern)
CONTEXT_BUDGETS = {
    "simple_task": 2000,      # ~$0.001-0.004
    "standard_task": 4000,    # ~$0.002-0.008
    "complex_task": 8000,     # ~$0.004-0.016
    "max_task": 16000,        # ~$0.008-0.032
}

# Model pricing (per million tokens) - for cost calculation
MODEL_PRICING = {
    "moonshotai/kimi-k2.5": {"input": 0.50, "output": 2.00},  # $0.50/$2.00 per million
    "qwen/qwen3.6-plus:free": {"input": 0.00, "output": 0.00},  # Free
    "qwen/qwen3-30b-a3b:free": {"input": 0.00, "output": 0.00},  # Free
    "qwen/qwen3-coder:free": {"input": 0.00, "output": 0.00},  # Free
    "anthropic/claude-sonnet-4-6": {"input": 3.00, "output": 15.00},  # $3/$15 per million
}


def _get_cache_key(prefix: str, content: str) -> str:
    """Generate deterministic cache key from content."""
    hash_input = f"{prefix}:{content}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:32]


def _call_ai(system: str, user: str, max_tokens: int = 4000, use_cache: bool = True, model: Optional[str] = None) -> str:
    """
    Call AI via OpenRouter with caching support.
    
    Args:
        system: System prompt
        user: User prompt  
        max_tokens: Max tokens to generate
        use_cache: Whether to check/save cache
        model: Optional model override (uses MODELS['default'] if not specified)
        
    Returns:
        Generated text
    """
    # Use specified model or default
    ai_model = model or MODELS["default"]
    
    # Check cache first
    cache_key = _get_cache_key("ai", f"{system}:{user}:{max_tokens}:{ai_model}")
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
        "model": ai_model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    
    # Track token usage
    token_usage = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": ai_model,
        "task": "unknown",  # Will be set by wrapper functions
        "cache_hit": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "prompt_length": len(system) + len(user),
        "max_tokens_requested": max_tokens,
    }
    
    try:
        response = httpx.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120.0,
        )
        
        # Log response status for debugging
        logger.info(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"OpenRouter error response: {response.text[:500]}")
            response.raise_for_status()
        
        data = response.json()
        
        # Extract token usage from response
        usage = data.get("usage", {})
        token_usage["input_tokens"] = usage.get("prompt_tokens", 0)
        token_usage["output_tokens"] = usage.get("completion_tokens", 0)
        token_usage["total_tokens"] = usage.get("total_tokens", 0)
        
        # Calculate cost
        pricing = MODEL_PRICING.get(ai_model, {"input": 0.50, "output": 2.00})
        input_cost = (token_usage["input_tokens"] / 1_000_000) * pricing["input"]
        output_cost = (token_usage["output_tokens"] / 1_000_000) * pricing["output"]
        token_usage["cost_usd"] = round(input_cost + output_cost, 6)
        
        # Log token usage
        _log_token_usage(token_usage)
        
        result = data["choices"][0]["message"]["content"]
        
        # Cache the result
        if use_cache:
            cache.set(cache_key, result, expire=86400 * 7)  # 7 days
            logger.info(f"AI cache saved: {cache_key[:8]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        token_usage["error"] = str(e)
        _log_token_usage(token_usage)
        
        # Circuit breaker: track consecutive failures (CSkill pattern)
        _circuit_breaker_state["consecutive_failures"] += 1
        if _circuit_breaker_state["consecutive_failures"] >= CIRCUIT_BREAKER_THRESHOLD:
            if not _circuit_breaker_state["tripped"]:
                logger.warning(f"CIRCUIT BREAKER TRIPPED: {CIRCUIT_BREAKER_THRESHOLD} consecutive failures")
                _circuit_breaker_state["tripped"] = True
                _circuit_breaker_state["last_trip_time"] = datetime.utcnow().isoformat()
        
        raise
    else:
        # Success: reset circuit breaker (CSkill pattern)
        if _circuit_breaker_state["consecutive_failures"] > 0:
            logger.info(f"Circuit breaker reset after {_circuit_breaker_state['consecutive_failures']} failures")
            _circuit_breaker_state["consecutive_failures"] = 0
            _circuit_breaker_state["tripped"] = False
            _circuit_breaker_state["last_trip_time"] = None


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
3. Header: "Your RivalEdge Weekly Brief" - include the actual date (not a placeholder)
4. ALWAYS include a "Competitor Snapshot" section for ALL competitors with:
   - Competitor name + URL as a section header
   - Current pricing (if known)
   - Top 3 features or value propositions
   - Their main positioning/tagline
5. For competitors WITH changes (has_changes=True): also show what changed this week
6. For competitors with NO changes: show the snapshot with a note "No changes detected this week"
7. Footer with: {{unsubscribe_url}} placeholder
8. Keep tone sharp and actionable — like a briefing from a sharp analyst
9. End with a "What to watch" section: 1-2 strategic observations about the competitive landscape

IMPORTANT: Use the actual current date provided in the prompt. Do NOT use placeholders like {{current_date}}."""


def generate_weekly_digest(user_email: str, competitors_with_diffs: list[dict]) -> str:
    """
    Generate a full HTML email digest for the user.
    Cached per user per week based on competitor data hash.
    """
    from datetime import datetime
    
    # Get current date for the digest
    current_date = datetime.now().strftime("%B %d, %Y")
    
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

CURRENT DATE: {current_date}

Summary: {change_count} competitor(s) with changes, {high_sig_count} high-significance.

COMPETITORS WITH CHANGES:
{chr(10).join(changed_sections) if changed_sections else "None this week."}

COMPETITORS WITH NO CHANGES:
{', '.join(unchanged_names) if unchanged_names else "None"}

Generate a complete HTML email following the system instructions. Use the CURRENT DATE ({current_date}) in the header, not a placeholder."""
    
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


# ── Task-Specific AI Functions ────────────────────────────────────────────────

def generate_sales_copy(prompt: str, max_tokens: int = 2000) -> str:
    """
    Generate sales copy using free Qwen model.
    For: cold emails, LinkedIn messages, outreach copy.
    """
    return _call_ai(
        system="You are a sales copywriter. Write concise, persuasive copy that gets responses. Focus on value, not features. Keep it under 150 words.",
        user=prompt,
        max_tokens=max_tokens,
        model=MODELS["sales"],
        use_cache=True,
    )


def generate_marketing_content(prompt: str, max_tokens: int = 4000) -> str:
    """
    Generate marketing content using free Qwen model.
    For: social media posts, blog content, landing page copy.
    """
    return _call_ai(
        system="You are a marketing content writer. Create engaging, shareable content. Use clear headlines, bullet points, and calls to action.",
        user=prompt,
        max_tokens=max_tokens,
        model=MODELS["marketing"],
        use_cache=True,
    )


def research_lead(prompt: str, max_tokens: int = 1500) -> str:
    """
    Research and analyze leads using free Qwen model.
    For: parsing LinkedIn profiles, company research, personalization hooks.
    """
    return _call_ai(
        system="You are a sales researcher. Extract key facts, pain points, and personalization angles. Be concise and factual.",
        user=prompt,
        max_tokens=max_tokens,
        model=MODELS["research"],
        use_cache=True,
    )


def generate_code(prompt: str, max_tokens: int = 4000) -> str:
    """
    Generate code using Kimi (high quality, paid).
    For: actual coding tasks, complex implementations.
    """
    return _call_ai(
        system="You are a senior software engineer. Write clean, well-documented code. Follow best practices.",
        user=prompt,
        max_tokens=max_tokens,
        model=MODELS["coding"],
        use_cache=True,
    )


# ── Circuit Breaker & Budget Management (CSkill Patterns) ─────────────────────

def check_circuit_breaker() -> Dict[str, Any]:
    """Check circuit breaker status."""
    return {
        "tripped": _circuit_breaker_state["tripped"],
        "consecutive_failures": _circuit_breaker_state["consecutive_failures"],
        "threshold": CIRCUIT_BREAKER_THRESHOLD,
        "last_trip_time": _circuit_breaker_state["last_trip_time"],
    }


def reset_circuit_breaker():
    """Manually reset circuit breaker."""
    _circuit_breaker_state["consecutive_failures"] = 0
    _circuit_breaker_state["tripped"] = False
    _circuit_breaker_state["last_trip_time"] = None
    logger.info("Circuit breaker manually reset")


def get_context_budget(task_type: str = "standard_task") -> int:
    """Get token budget for task type (CSkill pattern)."""
    return CONTEXT_BUDGETS.get(task_type, CONTEXT_BUDGETS["standard_task"])


def call_ai_with_budget(
    system: str,
    user: str,
    task_type: str = "standard_task",
    use_cache: bool = True,
    model: Optional[str] = None,
) -> str:
    """
    Call AI with context budget enforcement (CSkill pattern).
    
    Args:
        system: System prompt
        user: User prompt
        task_type: Budget category (simple_task, standard_task, complex_task, max_task)
        use_cache: Whether to use cache
        model: Optional model override
    """
    # Check circuit breaker first
    if _circuit_breaker_state["tripped"]:
        raise RuntimeError("Circuit breaker is tripped. Too many consecutive failures.")
    
    # Get budget for task type
    budget = get_context_budget(task_type)
    
    # Truncate if over budget (simple truncation strategy)
    combined_length = len(system) + len(user)
    if combined_length > budget * 4:  # Rough chars to tokens estimate
        logger.warning(f"Prompt length {combined_length} exceeds budget {budget * 4}, truncating")
        # Truncate user content, keep system intact
        max_user_chars = budget * 4 - len(system) - 100
        user = user[:max_user_chars] + "\n...[truncated]"
    
    return _call_ai(
        system=system,
        user=user,
        max_tokens=budget,
        use_cache=use_cache,
        model=model,
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


def get_model_info() -> dict:
    """Get current model configuration."""
    return {
        "models": MODELS,
        "default": MODELS["default"],
        "cost_optimized": {
            "sales": "qwen/qwen3.6-plus:free ($0)",
            "marketing": "qwen/qwen3.6-plus:free ($0)",
            "research": "qwen/qwen3-30b-a3b:free ($0)",
            "coding": "moonshotai/kimi-k2.5 (paid)",
        }
    }


# ── Token Usage Tracking ───────────────────────────────────────────────────────

def _log_token_usage(usage: Dict[str, Any]):
    """Log token usage to file for analysis."""
    try:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = TOKEN_LOG_DIR / f"token_usage_{date_str}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(usage) + "\n")
    except Exception as e:
        logger.error(f"Failed to log token usage: {e}")


def get_token_usage_stats(days: int = 7) -> Dict[str, Any]:
    """
    Get token usage statistics for the last N days.
    
    Returns:
        Dictionary with usage breakdown by model, task, and cost
    """
    stats = {
        "total_requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cost_usd": 0.0,
        "cache_hits": 0,
        "by_model": {},
        "by_task": {},
        "daily_breakdown": [],
    }
    
    try:
        for i in range(days):
            date = datetime.utcnow() - __import__('datetime').timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = TOKEN_LOG_DIR / f"token_usage_{date_str}.jsonl"
            
            if not log_file.exists():
                continue
            
            daily_stats = {
                "date": date_str,
                "requests": 0,
                "cost_usd": 0.0,
            }
            
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        stats["total_requests"] += 1
                        stats["total_input_tokens"] += entry.get("input_tokens", 0)
                        stats["total_output_tokens"] += entry.get("output_tokens", 0)
                        stats["total_cost_usd"] += entry.get("cost_usd", 0)
                        
                        if entry.get("cache_hit"):
                            stats["cache_hits"] += 1
                        
                        # By model
                        model = entry.get("model", "unknown")
                        if model not in stats["by_model"]:
                            stats["by_model"][model] = {
                                "requests": 0,
                                "cost_usd": 0.0,
                                "tokens": 0,
                            }
                        stats["by_model"][model]["requests"] += 1
                        stats["by_model"][model]["cost_usd"] += entry.get("cost_usd", 0)
                        stats["by_model"][model]["tokens"] += entry.get("total_tokens", 0)
                        
                        # By task
                        task = entry.get("task", "unknown")
                        if task not in stats["by_task"]:
                            stats["by_task"][task] = {
                                "requests": 0,
                                "cost_usd": 0.0,
                            }
                        stats["by_task"][task]["requests"] += 1
                        stats["by_task"][task]["cost_usd"] += entry.get("cost_usd", 0)
                        
                        # Daily
                        daily_stats["requests"] += 1
                        daily_stats["cost_usd"] += entry.get("cost_usd", 0)
                        
                    except json.JSONDecodeError:
                        continue
            
            stats["daily_breakdown"].append(daily_stats)
        
        # Round costs for readability
        stats["total_cost_usd"] = round(stats["total_cost_usd"], 4)
        for model in stats["by_model"]:
            stats["by_model"][model]["cost_usd"] = round(stats["by_model"][model]["cost_usd"], 4)
        for task in stats["by_task"]:
            stats["by_task"][task]["cost_usd"] = round(stats["by_task"][task]["cost_usd"], 4)
        for day in stats["daily_breakdown"]:
            day["cost_usd"] = round(day["cost_usd"], 4)
        
    except Exception as e:
        logger.error(f"Failed to get token stats: {e}")
    
    return stats


def audit_context_efficiency() -> Dict[str, Any]:
    """
    Audit context management for inefficiencies.
    
    Identifies:
    - High token count requests
    - Expensive models for simple tasks
    - Cache miss patterns
    - Prompt length issues
    """
    audit = {
        "inefficiencies": [],
        "recommendations": [],
        "summary": {},
    }
    
    try:
        # Get last 7 days of logs
        all_entries = []
        for i in range(7):
            date = datetime.utcnow() - __import__('datetime').timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = TOKEN_LOG_DIR / f"token_usage_{date_str}.jsonl"
            
            if log_file.exists():
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            all_entries.append(json.loads(line.strip()))
                        except:
                            continue
        
        if not all_entries:
            audit["summary"] = {"message": "No data available for audit"}
            return audit
        
        # Find inefficiencies
        high_token_requests = [e for e in all_entries if e.get("total_tokens", 0) > 10000]
        expensive_models = [e for e in all_entries if e.get("model", "").startswith("anthropic")]
        long_prompts = [e for e in all_entries if e.get("prompt_length", 0) > 50000]
        
        if high_token_requests:
            audit["inefficiencies"].append({
                "type": "high_token_usage",
                "count": len(high_token_requests),
                "description": f"{len(high_token_requests)} requests used >10K tokens",
                "examples": high_token_requests[:3],
            })
            audit["recommendations"].append("Consider truncating long contexts or using smaller models for simple tasks")
        
        if expensive_models:
            cost = sum(e.get("cost_usd", 0) for e in expensive_models)
            audit["inefficiencies"].append({
                "type": "expensive_model_usage",
                "count": len(expensive_models),
                "cost_usd": round(cost, 4),
                "description": f"Using expensive Anthropic models ({len(expensive_models)} calls, ${cost:.4f})",
            })
            audit["recommendations"].append("Switch to Kimi or Qwen for non-critical tasks")
        
        if long_prompts:
            audit["inefficiencies"].append({
                "type": "long_prompts",
                "count": len(long_prompts),
                "description": f"{len(long_prompts)} requests had >50K character prompts",
            })
            audit["recommendations"].append("Review prompt templates for unnecessary verbosity")
        
        # Summary
        total_cost = sum(e.get("cost_usd", 0) for e in all_entries)
        total_tokens = sum(e.get("total_tokens", 0) for e in all_entries)
        cache_hits = sum(1 for e in all_entries if e.get("cache_hit"))
        
        audit["summary"] = {
            "total_requests": len(all_entries),
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "cache_hit_rate": round(cache_hits / len(all_entries) * 100, 2) if all_entries else 0,
            "avg_cost_per_request": round(total_cost / len(all_entries), 6) if all_entries else 0,
        }
        
    except Exception as e:
        logger.error(f"Failed to audit context efficiency: {e}")
        audit["error"] = str(e)
    
    return audit
