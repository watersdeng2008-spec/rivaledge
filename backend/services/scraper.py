"""
Scraper service — fetches competitor page content.
Primary: Playwright (headless Chromium)
Fallback: Brave Search API (when JS rendering not needed)

Day 2 feature — stub with interface defined.
"""
import os
from typing import Optional


async def scrape_url(url: str) -> dict:
    """
    Scrape a URL and return structured content.
    
    Returns:
        {
            "url": str,
            "title": str,
            "description": str,
            "text": str,           # main body text
            "links": list[str],
            "scraped_at": str,     # ISO timestamp
            "method": str,         # "playwright" | "brave_api"
        }
    """
    # Try Playwright first
    try:
        return await _scrape_with_playwright(url)
    except Exception as e:
        # Fallback to Brave Search API
        try:
            return await _scrape_with_brave(url)
        except Exception as e2:
            return {
                "url": url,
                "title": "",
                "description": "",
                "text": "",
                "links": [],
                "scraped_at": _now(),
                "method": "failed",
                "error": str(e2),
            }


async def _scrape_with_playwright(url: str) -> dict:
    """Headless Chromium scrape via Playwright."""
    from playwright.async_api import async_playwright
    from datetime import datetime, timezone

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle", timeout=30000)
        
        title = await page.title()
        description = await page.evaluate(
            "document.querySelector('meta[name=description]')?.content || ''"
        )
        text = await page.evaluate("document.body?.innerText || ''")
        links = await page.evaluate(
            "[...document.querySelectorAll('a[href]')].map(a => a.href).slice(0, 50)"
        )
        
        await browser.close()
        
        return {
            "url": url,
            "title": title,
            "description": description,
            "text": text[:10000],  # Cap at 10k chars
            "links": links,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "method": "playwright",
        }


async def _scrape_with_brave(url: str) -> dict:
    """Fallback: Use Brave Search API to get page summary."""
    import httpx
    from datetime import datetime, timezone

    api_key = os.environ.get("BRAVE_SEARCH_API_KEY", "")
    if not api_key:
        raise RuntimeError("BRAVE_SEARCH_API_KEY not set")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            params={"q": f"site:{url}", "count": 1},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

    result = data.get("web", {}).get("results", [{}])[0]
    
    return {
        "url": url,
        "title": result.get("title", ""),
        "description": result.get("description", ""),
        "text": result.get("description", ""),
        "links": [],
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "method": "brave_api",
    }


def diff_snapshots(old: dict, new: dict) -> dict:
    """
    Compute a diff between two snapshots.
    Returns changes in title, description, and text.
    """
    changes = {}
    
    for field in ["title", "description", "text"]:
        old_val = old.get(field, "")
        new_val = new.get(field, "")
        if old_val != new_val:
            changes[field] = {
                "before": old_val[:500] if old_val else "",
                "after": new_val[:500] if new_val else "",
            }
    
    return changes


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
