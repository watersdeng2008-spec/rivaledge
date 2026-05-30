"""
GEO Audit Generator — Automated technical GEO audit + AI citation analysis.

Generates a complete GEO audit report for any client URL, including:
- Technical GEO assets (robots.txt, llms.txt, schema, sitemap)
- AI citation baseline (ChatGPT, Claude, Perplexity, Google AI, Bing Copilot)
- Competitor GEO posture
- 100-point GEO score
- Prioritized roadmap

Usage:
    from agents.geo_audit_generator import generate_geo_audit
    
    audit = generate_geo_audit(
        url="https://example.com",
        company_name="Example Inc",
        industry="saas",
        competitors=["competitor1.com", "competitor2.com"]
    )
"""

import os
import re
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict

import httpx
from bs4 import BeautifulSoup

from services.ai_recommendation_share import calculate_ars, ARSResult

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

# AI crawlers to check for
AI_CRAWLERS = [
    "GPTBot",
    "ChatGPT-User", 
    "ClaudeBot",
    "Claude-Web",
    "PerplexityBot",
    "Applebot-Extended",
    "Bytespider",
    "Google-Extended",
    "CCBot",
]

# Schema types to check for
SCHEMA_TYPES = [
    "Organization",
    "WebSite",
    "WebPage",
    "Product",
    "SoftwareApplication",
    "FAQPage",
    "BreadcrumbList",
    "BlogPosting",
    "Article",
    "LocalBusiness",
]

# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class TechnicalAudit:
    """Results of technical GEO asset audit."""
    robots_txt: Dict[str, Any]
    llms_txt: Dict[str, Any]
    sitemap: Dict[str, Any]
    schema: Dict[str, Any]
    crawler_access: Dict[str, Any]
    score: int  # 0-40


@dataclass
class AICitationAudit:
    """Results of AI citation baseline."""
    ars_result: Optional[ARSResult]
    queries_tested: int
    platforms_tested: List[str]
    score: int  # 0-30


@dataclass
class CompetitorAudit:
    """Results of competitor GEO posture audit."""
    competitors: List[Dict[str, Any]]
    score: int  # 0-20


@dataclass
class GEOAuditReport:
    """Complete GEO audit report."""
    company_name: str
    url: str
    industry: str
    audit_date: str
    overall_score: int  # 0-100
    grade: str  # A-F
    technical: TechnicalAudit
    ai_citations: AICitationAudit
    competitors: CompetitorAudit
    recommendations: List[Dict[str, Any]]
    roadmap: Dict[str, List[Dict[str, Any]]]


# ── Technical Audit Functions ────────────────────────────────────────────────

async def check_robots_txt(url: str) -> Dict[str, Any]:
    """Check robots.txt for AI crawler rules."""
    domain = extract_domain(url)
    robots_url = f"https://{domain}/robots.txt"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(robots_url)
            
        if response.status_code != 200:
            return {
                "present": False,
                "url": robots_url,
                "crawler_rules": {},
                "issues": ["robots.txt not found (404)"],
            }
        
        content = response.text
        crawler_rules = {}
        issues = []
        
        for crawler in AI_CRAWLERS:
            # Check if crawler is mentioned (case-insensitive User-agent)
            if crawler in content:
                # Check if allowed or disallowed
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if f"User-agent: {crawler}" in line or f"User-Agent: {crawler}" in line:
                        # Check next lines for Allow/Disallow
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].startswith("Allow:"):
                                crawler_rules[crawler] = "allowed"
                                break
                            elif lines[j].startswith("Disallow:"):
                                crawler_rules[crawler] = "disallowed"
                                issues.append(f"{crawler} is explicitly disallowed")
                                break
                        else:
                            # If no Allow/Disallow found after User-agent, check if it falls under general Allow
                            crawler_rules[crawler] = "allowed"
                        break
                else:
                    crawler_rules[crawler] = "allowed"  # Mentioned with general allow
            else:
                crawler_rules[crawler] = "not mentioned"
        
        return {
            "present": True,
            "url": robots_url,
            "crawler_rules": crawler_rules,
            "issues": issues,
        }
    
    except Exception as e:
        logger.error(f"Failed to check robots.txt for {url}: {e}")
        return {
            "present": False,
            "url": robots_url,
            "crawler_rules": {},
            "issues": [f"Error fetching robots.txt: {str(e)}"],
        }


async def check_llms_txt(url: str) -> Dict[str, Any]:
    """Check if llms.txt exists and analyze content."""
    domain = extract_domain(url)
    llms_url = f"https://{domain}/llms.txt"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(llms_url)
        
        if response.status_code != 200:
            return {
                "present": False,
                "url": llms_url,
                "content_length": 0,
                "sections": [],
                "issues": ["llms.txt not found (404) — highest priority fix"],
            }
        
        content = response.text
        sections = []
        issues = []
        
        # Check for key sections
        if "# " in content:
            sections.append("Title")
        if "## Product" in content or "## Features" in content:
            sections.append("Product/Features")
        if "## Pricing" in content:
            sections.append("Pricing")
        if "## Comparison" in content or "## Competitors" in content:
            sections.append("Comparison")
        if "## Contact" in content:
            sections.append("Contact")
        
        if len(sections) < 3:
            issues.append("llms.txt exists but missing key sections (pricing, comparison, contact)")
        
        return {
            "present": True,
            "url": llms_url,
            "content_length": len(content),
            "sections": sections,
            "issues": issues,
        }
    
    except Exception as e:
        logger.error(f"Failed to check llms.txt for {url}: {e}")
        return {
            "present": False,
            "url": llms_url,
            "content_length": 0,
            "sections": [],
            "issues": [f"Error fetching llms.txt: {str(e)}"],
        }


async def check_sitemap(url: str) -> Dict[str, Any]:
    """Check sitemap.xml for freshness and completeness."""
    domain = extract_domain(url)
    sitemap_url = f"https://{domain}/sitemap.xml"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(sitemap_url)
        
        if response.status_code != 200:
            return {
                "present": False,
                "url": sitemap_url,
                "url_count": 0,
                "last_modified": None,
                "issues": ["sitemap.xml not found (404)"],
            }
        
        content = response.text
        issues = []
        
        # Count URLs
        url_count = content.count("<url>")
        
        # Check for lastmod dates
        lastmod_matches = re.findall(r'<lastmod>(.*?)</lastmod>', content)
        last_modified = None
        
        if lastmod_matches:
            # Get most recent date
            try:
                dates = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in lastmod_matches]
                last_modified = max(dates).isoformat()
            except:
                pass
        else:
            issues.append("No lastmod dates in sitemap — AI crawlers prefer fresh content")
        
        if url_count < 10:
            issues.append(f"Only {url_count} URLs in sitemap — may be incomplete")
        
        return {
            "present": True,
            "url": sitemap_url,
            "url_count": url_count,
            "last_modified": last_modified,
            "issues": issues,
        }
    
    except Exception as e:
        logger.error(f"Failed to check sitemap for {url}: {e}")
        return {
            "present": False,
            "url": sitemap_url,
            "url_count": 0,
            "last_modified": None,
            "issues": [f"Error fetching sitemap: {str(e)}"],
        }


async def check_schema_markup(url: str) -> Dict[str, Any]:
    """Check for structured data (schema.org) on homepage."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code != 200:
            return {
                "present": False,
                "types_found": [],
                "types_missing": SCHEMA_TYPES,
                "issues": [f"Homepage returned {response.status_code}"],
            }
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for JSON-LD schema (including in Next.js streaming data)
        types_found = []
        
        # Method 1: Standard script tags
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        schema_type = data.get('@type', '')
                        if schema_type:
                            types_found.append(schema_type)
                        # Check @graph array
                        if '@graph' in data:
                            for item in data['@graph']:
                                schema_type = item.get('@type', '')
                                if schema_type:
                                    types_found.append(schema_type)
                    elif isinstance(data, list):
                        for item in data:
                            schema_type = item.get('@type', '')
                            if schema_type:
                                types_found.append(schema_type)
            except:
                continue
        
        # Method 2: Search raw HTML for schema.org types (for Next.js inline scripts)
        if not types_found:
            html_text = response.text
            # Look for @type declarations in the HTML
            type_matches = re.findall(r'"@type"\s*:\s*"([^"]+)"', html_text)
            types_found.extend(type_matches)
            # Look for @type in @graph
            graph_matches = re.findall(r'"@type"\s*:\s*"([^"]+)"', html_text)
            for match in graph_matches:
                if match not in types_found:
                    types_found.append(match)
        
        types_missing = [t for t in SCHEMA_TYPES if t not in types_found]
        issues = []
        
        if not types_found:
            issues.append("No schema markup found — critical for AI understanding")
        
        if "Organization" not in types_found:
            issues.append("Missing Organization schema — helps AI identify your brand")
        
        if "Product" not in types_found and "SoftwareApplication" not in types_found:
            issues.append("Missing Product/SoftwareApplication schema")
        
        return {
            "present": len(types_found) > 0,
            "types_found": types_found,
            "types_missing": types_missing,
            "issues": issues,
        }
    
    except Exception as e:
        logger.error(f"Failed to check schema for {url}: {e}")
        return {
            "present": False,
            "types_found": [],
            "types_missing": SCHEMA_TYPES,
            "issues": [f"Error checking schema: {str(e)}"],
        }


async def check_crawler_access(url: str) -> Dict[str, Any]:
    """Verify AI crawlers can actually access the site."""
    domain = extract_domain(url)
    results = {}
    issues = []
    
    test_crawlers = {
        "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.0; +https://openai.com/gptbot)",
        "ClaudeBot": "Mozilla/5.0 (compatible; ClaudeBot/1.0; +https://www.anthropic.com/claudebot)",
        "PerplexityBot": "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://www.perplexity.ai/perplexitybot)",
    }
    
    for crawler, user_agent in test_crawlers.items():
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"https://{domain}/",
                    headers={"User-Agent": user_agent},
                    follow_redirects=True
                )
            
            if response.status_code == 200:
                results[crawler] = "accessible"
            else:
                results[crawler] = f"blocked ({response.status_code})"
                issues.append(f"{crawler} gets HTTP {response.status_code}")
        
        except Exception as e:
            results[crawler] = f"error: {str(e)}"
            issues.append(f"{crawler} access error: {str(e)}")
    
    return {
        "results": results,
        "issues": issues,
    }


# ── Scoring Functions ────────────────────────────────────────────────────────

def calculate_technical_score(robots: Dict, llms: Dict, sitemap: Dict, schema: Dict, crawler: Dict) -> int:
    """Calculate technical GEO score (0-40)."""
    score = 0
    
    # robots.txt (10 points)
    if robots.get("present"):
        score += 5
        allowed_crawlers = sum(1 for v in robots.get("crawler_rules", {}).values() if v == "allowed")
        score += min(5, allowed_crawlers // 2)
    
    # llms.txt (10 points)
    if llms.get("present"):
        score += 5
        if len(llms.get("sections", [])) >= 4:
            score += 5
        elif len(llms.get("sections", [])) >= 2:
            score += 3
    
    # sitemap (5 points)
    if sitemap.get("present"):
        score += 3
        if sitemap.get("last_modified"):
            score += 2
    
    # schema (10 points)
    if schema.get("present"):
        score += 5
        types_found = len(schema.get("types_found", []))
        score += min(5, types_found)
    
    # crawler access (5 points)
    accessible = sum(1 for v in crawler.get("results", {}).values() if v == "accessible")
    score += min(5, accessible * 2)
    
    return min(40, score)


def calculate_ai_citation_score(ars_result: Optional[ARSResult]) -> int:
    """Calculate AI citation score (0-30)."""
    if not ars_result:
        return 0
    
    # Base score from ARS
    score = ars_result.ars_score * 0.2  # 0-20 points
    
    # Bonus for being cited at all
    if ars_result.brand_mentions > 0:
        score += 5
    
    # Bonus for high ranking
    if ars_result.ars_score >= 70:
        score += 5
    
    return min(30, int(score))


def calculate_competitor_score(competitors: List[Dict]) -> int:
    """Calculate competitor posture score (0-20)."""
    if not competitors:
        return 10  # Neutral if no competitors analyzed
    
    score = 0
    for comp in competitors:
        # Check if competitor has better GEO
        comp_score = 0
        if comp.get("llms_txt", {}).get("present"):
            comp_score += 5
        if comp.get("schema", {}).get("present"):
            comp_score += 5
        
        # If we match or beat competitor, we get points
        if comp_score <= 5:
            score += 5
        elif comp_score <= 10:
            score += 3
    
    return min(20, score)


def get_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ── Report Generation ────────────────────────────────────────────────────────

def generate_recommendations(technical: Dict, ai_citations: Dict, competitors: List[Dict]) -> List[Dict[str, Any]]:
    """Generate prioritized recommendations based on audit findings."""
    recommendations = []
    
    # Technical recommendations
    if not technical.get("llms_txt", {}).get("present"):
        recommendations.append({
            "priority": "CRITICAL",
            "category": "Technical",
            "action": "Create and deploy llms.txt",
            "impact": "Highest ROI GEO asset — tells AI exactly what you do",
            "effort": "30 minutes",
        })
    
    if not technical.get("robots_txt", {}).get("present"):
        recommendations.append({
            "priority": "HIGH",
            "category": "Technical",
            "action": "Create robots.txt with AI crawler rules",
            "impact": "Ensures AI crawlers can access your site",
            "effort": "15 minutes",
        })
    
    robots_issues = technical.get("robots_txt", {}).get("issues", [])
    for issue in robots_issues:
        if "disallowed" in issue.lower():
            recommendations.append({
                "priority": "HIGH",
                "category": "Technical",
                "action": f"Fix robots.txt: {issue}",
                "impact": "Blocking AI crawlers from indexing your content",
                "effort": "5 minutes",
            })
    
    if not technical.get("schema", {}).get("present"):
        recommendations.append({
            "priority": "HIGH",
            "category": "Technical",
            "action": "Add schema markup (Organization, Product, FAQ)",
            "impact": "Helps AI understand your business structure",
            "effort": "2-4 hours",
        })
    
    if not technical.get("sitemap", {}).get("present"):
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Technical",
            "action": "Create sitemap.xml with lastmod dates",
            "impact": "Helps AI crawlers discover fresh content",
            "effort": "30 minutes",
        })
    
    # AI citation recommendations
    if ai_citations.get("ars_result"):
        ars = ai_citations["ars_result"]
        if ars.ars_score < 50:
            recommendations.append({
                "priority": "HIGH",
                "category": "AI Visibility",
                "action": "Increase AI citation share — add comparison content",
                "impact": f"Currently cited in {ars.ars_score:.0f}% of relevant queries",
                "effort": "Ongoing",
            })
    
    # Competitor recommendations
    for comp in competitors:
        if comp.get("llms_txt", {}).get("present") and not technical.get("llms_txt", {}).get("present"):
            recommendations.append({
                "priority": "HIGH",
                "category": "Competitive",
                "action": f"{comp.get('domain')} has llms.txt — you don't",
                "impact": "Competitor is feeding AI structured data, you aren't",
                "effort": "30 minutes",
            })
    
    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))
    
    return recommendations


def generate_roadmap(recommendations: List[Dict]) -> Dict[str, List[Dict[str, Any]]]:
    """Generate 30/60/90-day roadmap from recommendations."""
    critical = [r for r in recommendations if r["priority"] == "CRITICAL"]
    high = [r for r in recommendations if r["priority"] == "HIGH"]
    medium = [r for r in recommendations if r["priority"] == "MEDIUM"]
    
    return {
        "days_1_30": critical + high[:3],
        "days_31_60": high[3:] + medium[:3],
        "days_61_90": medium[3:] + [
            {
                "priority": "MEDIUM",
                "category": "Monitoring",
                "action": "Monthly GEO audit and score tracking",
                "impact": "Track progress and identify new issues",
                "effort": "1 hour/month",
            }
        ],
    }


# ── Main Function ────────────────────────────────────────────────────────────

async def generate_geo_audit(
    url: str,
    company_name: str,
    industry: str,
    competitors: Optional[List[str]] = None,
    tier: str = "pro"
) -> GEOAuditReport:
    """
    Generate a complete GEO audit report.
    
    Args:
        url: Client website URL
        company_name: Company name
        industry: Industry/category
        competitors: List of competitor URLs (optional)
        tier: Subscription tier (solo, pro, enterprise)
    
    Returns:
        GEOAuditReport with complete analysis
    """
    logger.info(f"Starting GEO audit for {company_name} ({url})")
    
    # Step 1: Technical audit
    logger.info("Running technical audit...")
    robots = await check_robots_txt(url)
    llms = await check_llms_txt(url)
    sitemap = await check_sitemap(url)
    schema = await check_schema_markup(url)
    crawler = await check_crawler_access(url)
    
    technical_score = calculate_technical_score(robots, llms, sitemap, schema, crawler)
    
    technical = TechnicalAudit(
        robots_txt=robots,
        llms_txt=llms,
        sitemap=sitemap,
        schema=schema,
        crawler_access=crawler,
        score=technical_score,
    )
    
    # Step 2: AI citation audit
    logger.info("Running AI citation analysis...")
    try:
        ars_result = await calculate_ars(
            brand_name=company_name,
            category=industry,
            competitors=competitors or [],
            plan=tier,
        )
    except Exception as e:
        logger.error(f"ARS calculation failed: {e}")
        ars_result = None
    
    ai_score = calculate_ai_citation_score(ars_result)
    
    ai_citations = AICitationAudit(
        ars_result=ars_result,
        queries_tested=ars_result.total_queries if ars_result else 0,
        platforms_tested=["ChatGPT", "Claude", "Perplexity"],
        score=ai_score,
    )
    
    # Step 3: Competitor audit
    logger.info("Analyzing competitors...")
    competitor_data = []
    if competitors:
        for comp_url in competitors[:3]:  # Limit to 3 competitors
            comp_domain = extract_domain(comp_url)
            comp_llms = await check_llms_txt(comp_url)
            comp_schema = await check_schema_markup(comp_url)
            
            competitor_data.append({
                "domain": comp_domain,
                "url": comp_url,
                "llms_txt": comp_llms,
                "schema": comp_schema,
            })
    
    comp_score = calculate_competitor_score(competitor_data)
    
    competitors_audit = CompetitorAudit(
        competitors=competitor_data,
        score=comp_score,
    )
    
    # Step 4: Calculate overall score
    overall_score = technical_score + ai_score + comp_score
    
    # Step 5: Generate recommendations
    recommendations = generate_recommendations(
        {
            "robots_txt": robots,
            "llms_txt": llms,
            "sitemap": sitemap,
            "schema": schema,
        },
        {"ars_result": ars_result},
        competitor_data,
    )
    
    # Step 6: Generate roadmap
    roadmap = generate_roadmap(recommendations)
    
    report = GEOAuditReport(
        company_name=company_name,
        url=url,
        industry=industry,
        audit_date=datetime.now().isoformat(),
        overall_score=overall_score,
        grade=get_grade(overall_score),
        technical=technical,
        ai_citations=ai_citations,
        competitors=competitors_audit,
        recommendations=recommendations,
        roadmap=roadmap,
    )
    
    logger.info(f"GEO audit complete for {company_name}: {overall_score}/100 (Grade {get_grade(overall_score)})")
    
    return report


# ── Utility Functions ────────────────────────────────────────────────────────

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    url = url.replace("https://", "").replace("http://", "")
    url = url.split("/")[0]
    return url


def audit_to_dict(audit: GEOAuditReport) -> Dict[str, Any]:
    """Convert audit report to dictionary for JSON serialization."""
    return {
        "company_name": audit.company_name,
        "url": audit.url,
        "industry": audit.industry,
        "audit_date": audit.audit_date,
        "overall_score": audit.overall_score,
        "grade": audit.grade,
        "technical": {
            "score": audit.technical.score,
            "robots_txt": audit.technical.robots_txt,
            "llms_txt": audit.technical.llms_txt,
            "sitemap": audit.technical.sitemap,
            "schema": audit.technical.schema,
            "crawler_access": audit.technical.crawler_access,
        },
        "ai_citations": {
            "score": audit.ai_citations.score,
            "queries_tested": audit.ai_citations.queries_tested,
            "platforms_tested": audit.ai_citations.platforms_tested,
            "ars_result": asdict(audit.ai_citations.ars_result) if audit.ai_citations.ars_result else None,
        },
        "competitors": {
            "score": audit.competitors.score,
            "competitors": audit.competitors.competitors,
        },
        "recommendations": audit.recommendations,
        "roadmap": audit.roadmap,
    }


# ── CLI / Testing ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    
    async def test():
        audit = await generate_geo_audit(
            url="https://rivaledge.ai",
            company_name="RivalEdge",
            industry="competitive intelligence",
            competitors=["https://www.crayon.co", "https://www.kompyte.com"],
        )
        
        print(f"GEO Audit for {audit.company_name}")
        print(f"Score: {audit.overall_score}/100 (Grade {audit.grade})")
        print(f"Technical: {audit.technical.score}/40")
        print(f"AI Citations: {audit.ai_citations.score}/30")
        print(f"Competitors: {audit.competitors.score}/20")
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(audit.recommendations[:5], 1):
            print(f"{i}. [{rec['priority']}] {rec['action']}")
    
    asyncio.run(test())
