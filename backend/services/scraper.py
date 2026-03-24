"""
Scraper service — full production implementation.
Primary: Playwright (headless Chromium, async)
Fallback: Brave Search API (when Playwright fails or returns empty content)
"""
import os
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse


# ── Helpers ────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc or url
    except Exception:
        return url


def _truncate(text: str, max_chars: int = 5000) -> str:
    return text[:max_chars] if text else ""


def _extract_prices(text: str) -> list[str]:
    """Extract price strings like $29, $99/mo, $199/month, per month, etc."""
    patterns = [
        r'\$\d+(?:\.\d+)?(?:\s*/\s*(?:mo(?:nth)?|year|yr|week|day))?',
        r'\d+(?:\.\d+)?\s*(?:USD|EUR|GBP)\s*/\s*(?:mo(?:nth)?|year)',
        r'(?:free|free trial|freemium)',
        r'\$\d+\s+per\s+(?:month|year|user)',
    ]
    results = []
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        results.extend(matches)
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for m in results:
        key = m.lower().strip()
        if key not in seen:
            seen.add(key)
            deduped.append(m.strip())
    return deduped[:20]


def _extract_ctas(texts: list[str]) -> list[str]:
    """Filter button/link texts that look like CTAs."""
    cta_patterns = re.compile(
        r'\b(sign up|get started|try free|start free|free trial|start trial|'
        r'get started free|try it free|request demo|book demo|schedule demo|'
        r'contact us|learn more|see pricing|view pricing|buy now|subscribe|'
        r'create account|join free|join now|start now)\b',
        re.IGNORECASE
    )
    results = []
    seen = set()
    for t in texts:
        t = t.strip()
        if t and cta_patterns.search(t) and t.lower() not in seen:
            seen.add(t.lower())
            results.append(t)
    return results[:10]


# ── Playwright Scraper ─────────────────────────────────────────────────────────

async def _scrape_with_playwright(url: str) -> dict:
    """Full Playwright scrape with structured extraction."""
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )

        # Block images, fonts, media for speed
        async def block_resources(route, request):
            if request.resource_type in ("image", "font", "media", "stylesheet"):
                await route.abort()
            else:
                await route.continue_()

        page = await context.new_page()
        await page.route("**/*", block_resources)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            title = await page.title()
            html = await page.content()

        finally:
            await browser.close()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # Meta description
    meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    description = (meta_tag.get("content", "") if meta_tag else "").strip()

    # H1 / H2 headings
    headings = []
    for tag in soup.find_all(["h1", "h2"]):
        text = tag.get_text(separator=" ", strip=True)
        if text:
            headings.append(text)
    headings = headings[:20]

    # Extract main text
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    raw_text = soup.get_text(separator=" ", strip=True)
    raw_text = re.sub(r'\s+', ' ', raw_text).strip()

    # Word count (informational — not returned but used internally)
    # word_count = len(raw_text.split())

    # Pricing extraction
    pricing = _extract_prices(raw_text)

    # Feature lists — look for <ul>/<li> items
    features = []
    seen_features = set()
    # Look for lists that likely contain features
    for ul in soup.find_all(["ul", "ol"]):
        items = ul.find_all("li")
        if 2 <= len(items) <= 20:
            for li in items:
                text = li.get_text(separator=" ", strip=True)
                if text and len(text) > 5 and len(text) < 200:
                    key = text.lower()[:50]
                    if key not in seen_features:
                        seen_features.add(key)
                        features.append(text)
        if len(features) >= 30:
            break
    features = features[:30]

    # CTA buttons
    button_texts = []
    for btn in soup.find_all(["button", "a"]):
        text = btn.get_text(separator=" ", strip=True)
        if text and len(text) < 60:
            button_texts.append(text)
    ctas = _extract_ctas(button_texts)

    return {
        "url": url,
        "scraped_at": _now(),
        "title": title or "",
        "description": description,
        "pricing": pricing,
        "features": features,
        "headings": headings,
        "ctas": ctas,
        "raw_text": _truncate(raw_text, 5000),
        "source": "playwright",
    }


# ── Brave Search Fallback ──────────────────────────────────────────────────────

async def _scrape_with_brave(url: str) -> dict:
    """Fallback: Brave Search API snippets as content."""
    import httpx

    api_key = os.environ.get("BRAVE_SEARCH_API_KEY", "")
    if not api_key:
        raise RuntimeError("BRAVE_SEARCH_API_KEY not set")

    domain = _extract_domain(url)
    query = f"site:{domain} pricing features"

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
            params={"q": query, "count": 5},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("web", {}).get("results", [])

    # Aggregate snippets
    title = results[0].get("title", "") if results else ""
    description = results[0].get("description", "") if results else ""
    all_text = " ".join(r.get("description", "") for r in results)

    pricing = _extract_prices(all_text)
    features: list[str] = []
    headings: list[str] = []
    ctas: list[str] = []

    return {
        "url": url,
        "scraped_at": _now(),
        "title": title,
        "description": description,
        "pricing": pricing,
        "features": features,
        "headings": headings,
        "ctas": ctas,
        "raw_text": _truncate(all_text, 5000),
        "source": "brave_fallback",
    }


# ── Public API ─────────────────────────────────────────────────────────────────

async def scrape_url(url: str) -> dict:
    """
    Scrape a competitor URL. Tries Playwright first, falls back to Brave Search.

    Returns:
        {
            "url": str,
            "scraped_at": str,        # ISO timestamp
            "title": str,
            "description": str,
            "pricing": list[str],     # extracted price strings
            "features": list[str],    # feature bullets
            "headings": list[str],    # H1/H2
            "ctas": list[str],        # CTA button texts
            "raw_text": str,          # full page text (max 5000 chars)
            "source": "playwright" | "brave_fallback"
        }
    """
    try:
        result = await _scrape_with_playwright(url)
        # If Playwright returned near-empty content, try Brave
        content_len = len(result.get("raw_text", ""))
        if content_len < 50:
            raise ValueError(f"Playwright returned near-empty content ({content_len} chars)")
        return result
    except Exception:
        try:
            return await _scrape_with_brave(url)
        except Exception as e2:
            # Return a minimal failed result rather than crashing
            return {
                "url": url,
                "scraped_at": _now(),
                "title": "",
                "description": "",
                "pricing": [],
                "features": [],
                "headings": [],
                "ctas": [],
                "raw_text": "",
                "source": "brave_fallback",
                "error": str(e2),
            }


# ── Legacy diff helper (kept for backward compat) ──────────────────────────────

def diff_snapshots(old: dict, new: dict) -> dict:
    """
    Legacy diff helper (simple field-level comparison).
    For the rich diff with significance levels, use services.differ.diff_snapshots.
    """
    changes = {}
    for field in ["title", "description", "text", "raw_text"]:
        old_val = old.get(field, "")
        new_val = new.get(field, "")
        if old_val != new_val:
            changes[field] = {
                "before": old_val[:500] if old_val else "",
                "after": new_val[:500] if new_val else "",
            }
    return changes
