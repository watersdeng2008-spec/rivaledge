"""
AI Recommendation Share (ARS) Engine

Calculates what percentage of AI buying conversations include a brand
vs. its competitors across multiple AI models.

This is RivalEdge's signature metric — the "Domain Authority" equivalent
for AI search visibility.
"""

import os
import json
import logging
from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from collections import defaultdict

import httpx

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_MODELS = [
    "openai/gpt-4o",
    "perplexity/sonar",
    "anthropic/claude-sonnet-4",
]

# For paid tiers, add more models
ENTERPRISE_MODELS = [
    "openai/gpt-4o",
    "perplexity/sonar",
    "anthropic/claude-sonnet-4",
    "google/gemini-2.5-pro",
    "microsoft/llama-3.1",
]

# Number of prompts per audit
SOLO_PROMPTS = 10
PRO_PROMPTS = 20
ENTERPRISE_PROMPTS = 50

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class ARSResult:
    """Result of an AI Recommendation Share calculation."""
    brand_name: str
    category: str
    ars_score: float  # 0-100
    total_queries: int
    brand_mentions: int
    competitor_scores: dict  # {competitor_name: score}
    query_breakdown: list  # Detailed per-query results
    calculated_at: str
    period: str = "weekly"


@dataclass
class QueryResult:
    """Result for a single prompt across all models."""
    prompt: str
    model_results: dict  # {model: response_text}
    brand_mentioned: bool
    competitors_mentioned: dict  # {competitor: bool}
    recommendation_rank: Optional[int]  # 1st, 2nd, 3rd recommendation, etc.


# ── Prompt Generation ────────────────────────────────────────────────────────

ARS_PROMPT_GENERATOR_SYSTEM = """You are an expert at generating realistic buyer research prompts for AI search.

Given a product category and brand name, generate {count} high-intent buying prompts that a potential customer would ask ChatGPT, Perplexity, or Claude when researching solutions in this category.

Requirements:
1. Mix of comparison, recommendation, and best-of prompts
2. Include specific use cases and segments
3. Include price-sensitive and feature-specific queries
4. Make prompts natural — how real people actually ask AI
5. Some prompts should mention competitors by category, not by name

Output format: JSON array of strings only.
Example: ["Best project management software for remote teams", "Asana vs Monday.com for startups"]

Generate exactly {count} prompts."""


def generate_prompts(category: str, brand_name: str, count: int = 20) -> list[str]:
    """Generate high-intent buying prompts for a category."""
    import random
    
    # Seed prompts by category type
    prompt_templates = {
        "software": [
            "Best {category} for {segment}",
            "{brand} vs {competitor} for {use_case}",
            "Most affordable {category}",
            "{category} with {feature}",
            "Top rated {category} 2026",
            "{category} for {segment} comparison",
            "What is the best {category} for {use_case}?",
            "{brand} alternatives",
            "{category} ROI and pricing",
            "Enterprise {category} solutions",
        ],
        "service": [
            "Best {category} near me",
            "{category} reviews and ratings",
            "Affordable {category} for {segment}",
            "{brand} vs competitors",
            "Top {category} companies 2026",
            "{category} for {use_case}",
            "How much does {category} cost",
            "{category} with best reviews",
        ],
        "product": [
            "Best {category} for {segment}",
            "{brand} vs {competitor}",
            "{category} buying guide",
            "Top rated {category} 2026",
            "{category} with {feature}",
            "Affordable {category} options",
            "{category} reviews and comparisons",
        ],
    }
    
    # Determine category type
    category_lower = category.lower()
    if any(word in category_lower for word in ["software", "tool", "platform", "app", "saas"]):
        cat_type = "software"
    elif any(word in category_lower for word in ["service", "agency", "consulting", "firm"]):
        cat_type = "service"
    else:
        cat_type = "product"
    
    templates = prompt_templates.get(cat_type, prompt_templates["software"])
    
    # Fill in templates
    segments = ["small business", "startups", "enterprise", "remote teams", "freelancers", "nonprofits"]
    use_cases = ["scaling", "automation", "reporting", "collaboration", "analytics"]
    features = ["API", "integrations", "mobile app", "automation", "reporting"]
    competitors = ["competitors", "alternatives", "other options"]
    
    prompts = []
    for template in templates:
        prompt = template.format(
            category=category,
            brand=brand_name,
            segment=random.choice(segments),
            use_case=random.choice(use_cases),
            feature=random.choice(features),
            competitor=random.choice(competitors),
        )
        prompts.append(prompt)
    
    # Add some specific comparison prompts
    prompts.extend([
        f"What are the best {category} options?",
        f"{brand_name} review — is it worth it?",
        f"Compare top {category} solutions",
        f"Which {category} do experts recommend?",
    ])
    
    # Return unique prompts up to count
    unique_prompts = list(dict.fromkeys(prompts))[:count]
    
    # If we need more, generate variations
    while len(unique_prompts) < count:
        base = random.choice(unique_prompts)
        variation = base.replace("best", "top rated").replace("2026", "this year")
        if variation not in unique_prompts:
            unique_prompts.append(variation)
    
    return unique_prompts[:count]


# ── AI Query Execution ───────────────────────────────────────────────────────

async def query_ai_model(prompt: str, model: str, api_key: str) -> str:
    """Query a single AI model via OpenRouter."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://rivaledge.ai",
                    "X-Title": "RivalEdge ARS Engine",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Answer the user's question directly and concisely."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"AI query failed for {model}: {e}")
            return ""


# ── Mention Extraction ───────────────────────────────────────────────────────

def extract_mentions(response_text: str, brand_name: str, competitors: list[str]) -> dict:
    """Extract brand and competitor mentions from AI response."""
    text_lower = response_text.lower()
    brand_lower = brand_name.lower()
    
    # Check for brand mention
    brand_mentioned = brand_lower in text_lower
    
    # Check for competitor mentions
    competitors_mentioned = {}
    for comp in competitors:
        comp_lower = comp.lower()
        competitors_mentioned[comp] = comp_lower in text_lower
    
    # Determine recommendation rank (rough heuristic)
    recommendation_rank = None
    if brand_mentioned:
        # Find position of brand mention in text
        pos = text_lower.find(brand_lower)
        # Earlier mentions = higher rank
        if pos < 200:
            recommendation_rank = 1
        elif pos < 500:
            recommendation_rank = 2
        elif pos < 1000:
            recommendation_rank = 3
        else:
            recommendation_rank = 4
    
    return {
        "brand_mentioned": brand_mentioned,
        "competitors_mentioned": competitors_mentioned,
        "recommendation_rank": recommendation_rank,
    }


# ── ARS Calculation ──────────────────────────────────────────────────────────

async def calculate_ars(
    brand_name: str,
    category: str,
    competitors: list[str],
    plan: str = "pro",
    api_key: Optional[str] = None,
) -> ARSResult:
    """
    Calculate AI Recommendation Share for a brand.
    
    Args:
        brand_name: Name of the brand to analyze
        category: Product category (e.g., "project management software")
        competitors: List of competitor names
        plan: Subscription tier (solo, pro, enterprise)
        api_key: OpenRouter API key (defaults to env var)
    
    Returns:
        ARSResult with scores and breakdown
    """
    api_key = api_key or OPENROUTER_API_KEY
    if not api_key:
        raise ValueError("OpenRouter API key required")
    
    # Determine configuration based on plan
    if plan == "solo":
        prompt_count = SOLO_PROMPTS
        models = DEFAULT_MODELS[:2]  # 2 models
    elif plan == "enterprise":
        prompt_count = ENTERPRISE_PROMPTS
        models = ENTERPRISE_MODELS
    else:  # pro
        prompt_count = PRO_PROMPTS
        models = DEFAULT_MODELS
    
    # Generate prompts
    prompts = generate_prompts(category, brand_name, prompt_count)
    
    # Query AI models
    total_queries = len(prompts) * len(models)
    brand_mentions = 0
    competitor_mentions = defaultdict(int)
    query_breakdown = []
    
    logger.info(f"Calculating ARS for {brand_name} in {category}")
    logger.info(f"Queries: {len(prompts)} prompts × {len(models)} models = {total_queries} total")
    
    for prompt in prompts:
        model_results = {}
        prompt_brand_mentioned = False
        prompt_competitors = defaultdict(bool)
        
        for model in models:
            response = await query_ai_model(prompt, model, api_key)
            model_results[model] = response
            
            # Extract mentions
            mentions = extract_mentions(response, brand_name, competitors)
            
            if mentions["brand_mentioned"]:
                prompt_brand_mentioned = True
                brand_mentions += 1
            
            for comp, mentioned in mentions["competitors_mentioned"].items():
                if mentioned:
                    prompt_competitors[comp] = True
                    competitor_mentions[comp] += 1
        
        query_breakdown.append({
            "prompt": prompt,
            "model_results": model_results,
            "brand_mentioned": prompt_brand_mentioned,
            "competitors_mentioned": dict(prompt_competitors),
        })
    
    # Calculate ARS score
    ars_score = (brand_mentions / total_queries) * 100 if total_queries > 0 else 0
    
    # Calculate competitor scores
    competitor_scores = {}
    for comp in competitors:
        comp_score = (competitor_mentions[comp] / total_queries) * 100
        competitor_scores[comp] = round(comp_score, 2)
    
    result = ARSResult(
        brand_name=brand_name,
        category=category,
        ars_score=round(ars_score, 2),
        total_queries=total_queries,
        brand_mentions=brand_mentions,
        competitor_scores=competitor_scores,
        query_breakdown=query_breakdown,
        calculated_at=datetime.now(timezone.utc).isoformat(),
        period="weekly",
    )
    
    logger.info(f"ARS calculation complete: {brand_name} = {ars_score:.1f}%")
    return result


# ── Free Audit (Simplified) ──────────────────────────────────────────────────

async def calculate_free_audit_ars(
    brand_name: str,
    category: str,
    competitors: list[str],
    api_key: Optional[str] = None,
) -> dict:
    """
    Calculate a simplified ARS for the free audit tool.
    Uses fewer prompts/models for speed and cost efficiency.
    """
    api_key = api_key or OPENROUTER_API_KEY
    
    # Free audit: 5 prompts, 2 models = 10 queries
    prompts = generate_prompts(category, brand_name, 5)
    models = ["openai/gpt-4o", "perplexity/sonar"]
    
    total_queries = len(prompts) * len(models)
    brand_mentions = 0
    competitor_mentions = defaultdict(int)
    
    for prompt in prompts:
        for model in models:
            response = await query_ai_model(prompt, model, api_key)
            mentions = extract_mentions(response, brand_name, competitors)
            
            if mentions["brand_mentioned"]:
                brand_mentions += 1
            
            for comp, mentioned in mentions["competitors_mentioned"].items():
                if mentioned:
                    competitor_mentions[comp] += 1
    
    ars_score = (brand_mentions / total_queries) * 100 if total_queries > 0 else 0
    
    # Build ranking
    all_scores = {brand_name: ars_score}
    for comp in competitors:
        all_scores[comp] = (competitor_mentions[comp] / total_queries) * 100
    
    ranking = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "brand_name": brand_name,
        "category": category,
        "ars_score": round(ars_score, 1),
        "total_queries": total_queries,
        "brand_mentions": brand_mentions,
        "ranking": [
            {"rank": i + 1, "brand": name, "ars": round(score, 1)}
            for i, (name, score) in enumerate(ranking)
        ],
        "competitor_scores": {
            comp: round((competitor_mentions[comp] / total_queries) * 100, 1)
            for comp in competitors
        },
        "calculated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Database Storage ─────────────────────────────────────────────────────────

def save_ars_result(result: ARSResult, user_id: str) -> dict:
    """Save ARS result to Supabase."""
    import db.supabase as db
    
    payload = {
        "user_id": user_id,
        "brand_name": result.brand_name,
        "category": result.category,
        "ars_score": result.ars_score,
        "total_queries": result.total_queries,
        "brand_mentions": result.brand_mentions,
        "competitor_scores": result.competitor_scores,
        "query_breakdown": result.query_breakdown,
        "calculated_at": result.calculated_at,
        "period": result.period,
    }
    
    # Insert into ai_recommendation_share table
    r = httpx.post(
        db._url("ai_recommendation_share"),
        json=payload,
        headers=db._headers(),
        timeout=10,
    )
    
    if r.status_code >= 400:
        logger.error(f"Failed to save ARS result: {r.text[:500]}")
        raise Exception(f"Failed to save ARS: {r.status_code}")
    
    data = r.json()
    return data[0] if isinstance(data, list) and data else payload


def get_ars_history(user_id: str, brand_name: str, limit: int = 12) -> list:
    """Get ARS history for a brand."""
    import db.supabase as db
    
    r = httpx.get(
        db._url(f"ai_recommendation_share?user_id=eq.{user_id}&brand_name=eq.{brand_name}&order=calculated_at.desc&limit={limit}"),
        headers=db._headers(),
        timeout=10,
    )
    
    if r.status_code >= 400:
        logger.error(f"Failed to get ARS history: {r.text[:500]}")
        return []
    
    data = r.json()
    return data if isinstance(data, list) else []


# ── Export ───────────────────────────────────────────────────────────────────

def ars_to_dict(result: ARSResult) -> dict:
    """Convert ARSResult to dictionary for JSON serialization."""
    return asdict(result)
