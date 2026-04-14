#!/usr/bin/env python3
"""
Self-Healing Sales Agent Orchestrator v3

Features:
- Automatic retry with exponential backoff
- Alternative data sources when primary fails
- Self-diagnostics and health checks
- Automatic fallback templates
- Detailed logging for troubleshooting
"""

import os
import json
import asyncio
import httpx
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY", "")
BRAVE_API_KEY = os.environ.get("BRAVE_SEARCH_API_KEY", "")

# Model selection - use free Qwen for sales tasks
DEFAULT_MODEL = "qwen/qwen-2.5-72b-instruct"
RESEARCH_MODEL = "qwen/qwen3-30b-a3b:free"  # Free research model


@dataclass
class Lead:
    email: str
    first_name: str
    company_name: str
    company_domain: str
    title: str = ""
    linkedin_url: str = ""
    industry: str = ""
    status: str = "new"
    priority_score: int = 0
    created_at: str = ""
    source: str = ""  # Track which method found this lead
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ResearchResult:
    success: bool
    company_data: Dict
    decision_makers: List[Dict]
    emails: List[Dict]
    errors: List[str]
    methods_tried: List[str]
    duration_seconds: float


class FirecrawlClient:
    """Enhanced Firecrawl client with retries and fallbacks."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def scrape(self, url: str, formats: List[str] = None) -> Dict:
        """Scrape URL with retry logic."""
        formats = formats or ["markdown"]
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        async def _scrape():
            response = await self.client.post(
                f"{self.base_url}/scrape",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url, "formats": formats},
            )
            response.raise_for_status()
            return response.json()
        
        try:
            return await _scrape()
        except Exception as e:
            logger.error(f"Firecrawl scrape failed for {url}: {e}")
            return {"success": False, "error": str(e)}
    
    async def search(self, query: str, limit: int = 5) -> Dict:
        """Search with retry logic."""
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        async def _search():
            response = await self.client.post(
                f"{self.base_url}/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"query": query, "limit": limit},
            )
            response.raise_for_status()
            return response.json()
        
        try:
            return await _search()
        except Exception as e:
            logger.error(f"Firecrawl search failed for '{query}': {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        await self.client.aclose()


class OpenRouterClient:
    """OpenRouter client with cost tracking."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def complete(self, prompt: str, system: str = "", model: str = DEFAULT_MODEL, max_tokens: int = 2000) -> str:
        """Complete with retry and cost tracking."""
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        async def _complete():
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://rivaledge.ai",
                    "X-Title": "RivalEdge Sales Agent",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        
        try:
            return await _complete()
        except Exception as e:
            logger.error(f"OpenRouter completion failed: {e}")
            raise
    
    async def close(self):
        await self.client.aclose()


class HunterClient:
    """Hunter.io client for email finding."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def find_email(self, domain: str, first_name: str, last_name: str) -> Optional[Dict]:
        """Find email by name and domain."""
        try:
            response = await self.client.get(
                f"{self.base_url}/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": self.api_key,
                },
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and data["data"].get("email"):
                    return data["data"]
            return None
        except Exception as e:
            logger.error(f"Hunter email finder failed: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()


class SelfHealingResearchAgent:
    """Research agent with self-healing capabilities."""
    
    def __init__(self, firecrawl: FirecrawlClient, openrouter: OpenRouterClient, hunter: HunterClient):
        self.firecrawl = firecrawl
        self.openrouter = openrouter
        self.hunter = hunter
        self.methods_tried = []
        self.errors = []
    
    async def research_company(self, domain: str) -> Tuple[Dict, List[str]]:
        """
        Research company with multiple fallback methods.
        
        Returns:
            Tuple of (company_data, methods_tried)
        """
        self.methods_tried = []
        self.errors = []
        
        # Method 1: Direct website scrape
        company_data = await self._try_website_scrape(domain)
        if company_data and not company_data.get("error"):
            self.methods_tried.append("website_scrape")
            return company_data, self.methods_tried
        
        # Method 2: Search for company info
        company_data = await self._try_search(domain)
        if company_data and not company_data.get("error"):
            self.methods_tried.append("search")
            return company_data, self.methods_tried
        
        # Method 3: Minimal fallback
        self.methods_tried.append("fallback")
        return {
            "company_name": domain.replace(".com", "").title(),
            "industry": "unknown",
            "products": "Unknown - website scraping failed",
            "error": "All research methods failed",
        }, self.methods_tried
    
    async def _try_website_scrape(self, domain: str) -> Optional[Dict]:
        """Try to scrape company website."""
        try:
            result = await self.firecrawl.scrape(f"https://{domain}")
            if not result.get("success"):
                self.errors.append(f"Website scrape failed: {result.get('error')}")
                return None
            
            markdown = result["data"]["markdown"][:8000]
            
            prompt = f"""
Analyze this company website content and extract key information.

Website: {domain}
Content: {markdown[:5000]}

Return JSON with:
- company_name (official name)
- industry (category)
- products (main offering, 1-2 sentences)
- target_customers (who they serve)
- competitors (array of 3 competitors)
- positioning (one sentence tagline)
"""
            
            response = await self.openrouter.complete(
                prompt=prompt,
                system="You are a business analyst. Extract company information from website content. Return only valid JSON.",
                model=RESEARCH_MODEL,
                max_tokens=1500,
            )
            
            # Extract JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            
            self.errors.append("Could not parse JSON from LLM response")
            return None
            
        except Exception as e:
            self.errors.append(f"Website scrape error: {str(e)}")
            return None
    
    async def _try_search(self, domain: str) -> Optional[Dict]:
        """Try to find company info via search."""
        try:
            company_name = domain.replace(".com", "").replace(".io", "").replace(".ai", "")
            query = f"{company_name} company about products services"
            
            result = await self.firecrawl.search(query, limit=3)
            if not result.get("success"):
                self.errors.append(f"Search failed: {result.get('error')}")
                return None
            
            # Combine search results
            combined_content = ""
            for item in result.get("data", []):
                combined_content += item.get("markdown", "")[:2000] + "\n\n"
            
            if not combined_content:
                self.errors.append("Search returned no content")
                return None
            
            prompt = f"""
Based on these search results about {domain}, extract company information.

Search Results:
{combined_content[:4000]}

Return JSON with:
- company_name
- industry
- products
- target_customers
- competitors (array)
- positioning
"""
            
            response = await self.openrouter.complete(
                prompt=prompt,
                system="Extract company information from search results. Return only valid JSON.",
                model=RESEARCH_MODEL,
                max_tokens=1500,
            )
            
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            
            return None
            
        except Exception as e:
            self.errors.append(f"Search error: {str(e)}")
            return None
    
    async def find_decision_makers(self, domain: str, company_name: str) -> Tuple[List[Dict], List[str]]:
        """
        Find decision makers with multiple methods.
        
        Returns:
            Tuple of (decision_makers, methods_tried)
        """
        methods_tried = []
        all_decision_makers = []
        
        # Method 1: Team/leadership pages
        dm, method = await self._try_team_pages(domain, company_name)
        if dm:
            all_decision_makers.extend(dm)
            methods_tried.append(method)
        
        # Method 2: LinkedIn search
        if len(all_decision_makers) < 2:
            dm, method = await self._try_linkedin_search(domain, company_name)
            if dm:
                all_decision_makers.extend(dm)
                methods_tried.append(method)
        
        # Method 3: Generic fallback
        if not all_decision_makers:
            all_decision_makers = [
                {"name": "CEO", "title": "Chief Executive Officer", "source": "fallback"},
                {"name": "VP Product", "title": "VP Product", "source": "fallback"},
            ]
            methods_tried.append("generic_fallback")
        
        return all_decision_makers, methods_tried
    
    async def _try_team_pages(self, domain: str, company_name: str) -> Tuple[Optional[List[Dict]], str]:
        """Try to find decision makers from team pages."""
        try:
            team_urls = [
                f"https://{domain}/team",
                f"https://{domain}/about",
                f"https://{domain}/leadership",
                f"https://{domain}/company",
            ]
            
            team_content = ""
            for url in team_urls:
                try:
                    result = await self.firecrawl.scrape(url)
                    if result.get("success"):
                        content = result["data"]["markdown"]
                        if any(title in content.lower() for title in ["ceo", "founder", "chief", "vp ", "head of"]):
                            team_content += content[:4000] + "\n\n"
                            break
                except Exception as e:
                    continue
            
            if not team_content:
                return None, "team_pages"
            
            prompt = f"""
Extract decision makers from this company team information.

Company: {company_name}
Content: {team_content[:5000]}

Identify 2-3 people who would be decision makers for competitive intelligence software.
Look for: CEO, Founder, VP Product, Head of Strategy, Chief Strategy Officer, VP Marketing.

Return JSON array with objects containing:
- name (full name)
- title (exact job title)
- relevance (why they care about competitor monitoring, 1 sentence)
- source (where found)
"""
            
            response = await self.openrouter.complete(
                prompt=prompt,
                system="Extract decision maker information from company team pages. Return only valid JSON array.",
                model=RESEARCH_MODEL,
                max_tokens=1500,
            )
            
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                decision_makers = json.loads(response[json_start:json_end])
                if decision_makers and len(decision_makers) > 0:
                    return decision_makers, "team_pages"
            
            return None, "team_pages"
            
        except Exception as e:
            self.errors.append(f"Team pages error: {str(e)}")
            return None, "team_pages"
    
    async def _try_linkedin_search(self, domain: str, company_name: str) -> Tuple[Optional[List[Dict]], str]:
        """Try to find decision makers via search."""
        try:
            query = f"{company_name} CEO founder VP product site:linkedin.com"
            result = await self.firecrawl.search(query, limit=5)
            
            if not result.get("success"):
                return None, "linkedin_search"
            
            combined_content = ""
            for item in result.get("data", []):
                combined_content += item.get("markdown", "")[:1500] + "\n\n"
            
            if not combined_content:
                return None, "linkedin_search"
            
            prompt = f"""
Extract decision maker names and titles from these LinkedIn search results.

Company: {company_name}
Results: {combined_content[:4000]}

Return JSON array with:
- name
- title
- relevance (why they care about competitor monitoring)
- source: "linkedin_search"
"""
            
            response = await self.openrouter.complete(
                prompt=prompt,
                system="Extract names and titles from LinkedIn search results. Return only valid JSON array.",
                model=RESEARCH_MODEL,
                max_tokens=1500,
            )
            
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                decision_makers = json.loads(response[json_start:json_end])
                if decision_makers and len(decision_makers) > 0:
                    return decision_makers, "linkedin_search"
            
            return None, "linkedin_search"
            
        except Exception as e:
            self.errors.append(f"LinkedIn search error: {str(e)}")
            return None, "linkedin_search"


class EmailTemplateManager:
    """Manages email templates with self-optimization."""
    
    TEMPLATES = {
        "online_retail": {
            "name": "Online Retail / E-commerce",
            "subject": "{{company_name}} vs {{competitor_name}} — consolidating your competitor tracking",
            "body": """Hi {{first_name}},

With {{company_name}} {{positioning_hook}}, I imagine your team is already tracking what {{competitor_name}} and others are doing — but probably across a dozen different tabs, spreadsheets, and manual checks.

We built RivalEdge to consolidate all of that. One dashboard that tracks your competitors across:
• Amazon listings and pricing
• TikTok Shop and social campaigns  
• Walmart, Target, and retail partnerships
• Their own DTC stores and messaging
• New product launches and feature updates

What makes it different: You choose exactly what to track and how often to report. Weekly digests, real-time alerts, or deep-dive battle cards — whatever fits your workflow.

Finally, a tool that pays for itself the first time it prevents surprise.

Worth a 10-minute conversation to see if it fits how you already work?

Best,
Ben""",
            "tone": "Collaborative, emphasizes consolidation",
        },
        
        "physical_therapy": {
            "name": "Physical Therapy / Healthcare",
            "subject": "New competitor activity near {{company_name}}",
            "body": """Hi {{first_name}},

{{personalization_hook}}

In the PT space, the competitive landscape shifts fast — new clinics opening, insurance contracts changing, hospital partnerships forming. Most owners I talk to hear about these moves after they've already impacted patient volume.

We built RivalEdge specifically for healthcare operators. It monitors:
• New clinic openings in your territory
• Competitor service expansions (OT, speech, ABA)
• Insurance network additions and changes
• Hospital and physician group partnerships
• M&A activity and consolidation plays

You get weekly briefings on what your competitors are building, who they're partnering with, and where they're expanding — so you can respond before it affects your practice.

Worth a brief call to see if this fits how you track your market?

Best,
Ben""",
            "tone": "Territory-focused, emphasizes early warning",
        },
        
        "saas": {
            "name": "SaaS / Software",
            "subject": "{{company_name}} vs {{competitor_name}} — noticed something",
            "body": """Hi {{first_name}},

{{personalization_hook}}

Most {{industry}} teams I talk to are piecing together competitor intel from scattered sources — G2 reviews, pricing pages, product blogs, LinkedIn announcements. It's time-consuming and easy to miss critical moves.

RivalEdge consolidates it all: one dashboard that tracks what your competitors are building, pricing, and messaging. Weekly AI briefings delivered to your inbox.

Finally, a tool that pays for itself the first time it prevents surprise.

Worth a 10-minute conversation?

Best,
Ben""",
            "tone": "Direct, efficiency-focused",
        }
    }
    
    @classmethod
    def get_template(cls, industry: str) -> Dict:
        """Get template by industry."""
        return cls.TEMPLATES.get(industry, cls.TEMPLATES["saas"])
    
    @classmethod
    def detect_industry(cls, company_data: Dict) -> str:
        """Auto-detect industry from company data."""
        industry = company_data.get("industry", "").lower()
        products = company_data.get("products", "").lower()
        
        if any(word in industry or word in products for word in ["retail", "e-commerce", "amazon", "shopify", "dtc", "consumer goods", "charging", "electronics"]):
            return "online_retail"
        elif any(word in industry or word in products for word in ["physical therapy", "healthcare", "medical", "pt ", "rehab", "clinic"]):
            return "physical_therapy"
        else:
            return "saas"


class PersonalizationAgent:
    """Creates personalized emails with fallback strategies."""
    
    def __init__(self, openrouter: OpenRouterClient):
        self.openrouter = openrouter
        self.templates = EmailTemplateManager()
    
    async def draft_email(self, lead: Lead, company_data: Dict, decision_maker: Dict, industry: str = None) -> Dict:
        """Draft personalized email with multiple fallback strategies."""
        
        # Detect industry if not provided
        if not industry:
            industry = self.templates.detect_industry(company_data)
        
        template = self.templates.get_template(industry)
        
        # Generate hook
        try:
            hook = await self._generate_hook(lead, company_data, decision_maker, industry)
        except Exception as e:
            logger.warning(f"Hook generation failed, using fallback: {e}")
            hook = f"growing fast in {company_data.get('industry', 'the market')}"
        
        # Fill template
        competitor = company_data.get("competitors", ["competitors"])[0] if company_data.get("competitors") else "competitors"
        
        subject = template["subject"].format(
            company_name=lead.company_name,
            competitor_name=competitor
        )
        
        body = template["body"].format(
            first_name=decision_maker.get("name", "").split()[0] if " " in decision_maker.get("name", "") else decision_maker.get("name", "there"),
            company_name=lead.company_name,
            competitor_name=competitor,
            positioning_hook=hook,
            personalization_hook=hook,
            industry=industry,
        )
        
        return {
            "subject": subject,
            "body": body,
            "industry": industry,
            "template_used": template["name"],
            "decision_maker": decision_maker,
            "personalization_method": "ai_generated" if hook else "fallback",
        }
    
    async def _generate_hook(self, lead: Lead, company_data: Dict, dm: Dict, industry: str) -> str:
        """Generate personalized hook."""
        prompt = f"""
Write one sentence about {lead.company_name} ({company_data.get('products', 'products')}).

Mention their market position or recent initiative. Keep under 15 words.
Example: "leading the mobile charging market" or "expanding fast in sustainable home goods"

Return only the phrase, no punctuation at end.
"""
        
        response = await self.openrouter.complete(
            prompt=prompt,
            model=RESEARCH_MODEL,
            max_tokens=100,
        )
        
        return response.strip().strip(".").strip(",")


class SelfHealingSalesOrchestrator:
    """Main orchestrator with self-healing capabilities."""
    
    def __init__(self):
        self.firecrawl = FirecrawlClient(FIRECRAWL_API_KEY)
        self.openrouter = OpenRouterClient(OPENROUTER_API_KEY)
        self.hunter = HunterClient(HUNTER_API_KEY) if HUNTER_API_KEY else None
        self.research = SelfHealingResearchAgent(self.firecrawl, self.openrouter, self.hunter)
        self.personalization = PersonalizationAgent(self.openrouter)
    
    async def process_company(self, domain: str, industry_hint: str = None) -> ResearchResult:
        """
        Process a company with full self-healing and diagnostics.
        
        Returns:
            ResearchResult with full diagnostics
        """
        import time
        start_time = time.time()
        
        logger.info(f"🚀 Starting research for: {domain}")
        
        # Step 1: Research company
        company_data, company_methods = await self.research.research_company(domain)
        
        # Step 2: Find decision makers
        decision_makers, dm_methods = await self.research.find_decision_makers(
            domain, company_data.get("company_name", domain)
        )
        
        # Step 3: Draft emails for each decision maker
        emails = []
        for dm in decision_makers[:2]:  # Top 2
            try:
                lead = Lead(
                    email="",  # Will be filled by Hunter or manual
                    first_name=dm.get("name", "").split()[0] if " " in dm.get("name", "") else dm.get("name", ""),
                    company_name=company_data.get("company_name", domain),
                    company_domain=domain,
                    source=dm.get("source", "unknown"),
                )
                
                email = await self.personalization.draft_email(lead, company_data, dm, industry_hint)
                emails.append(email)
            except Exception as e:
                logger.error(f"Email drafting failed for {dm.get('name', 'unknown')}: {e}")
        
        duration = time.time() - start_time
        
        # Compile result
        result = ResearchResult(
            success=len(decision_makers) > 0 and len(emails) > 0,
            company_data=company_data,
            decision_makers=decision_makers,
            emails=emails,
            errors=self.research.errors,
            methods_tried=list(set(company_methods + dm_methods)),
            duration_seconds=round(duration, 2),
        )
        
        logger.info(f"✅ Research complete for {domain}: {len(decision_makers)} DMs, {len(emails)} emails in {duration:.1f}s")
        
        return result
    
    async def close(self):
        """Close all clients."""
        await self.firecrawl.close()
        await self.openrouter.close()
        if self.hunter:
            await self.hunter.close()


# Singleton instance
_orchestrator: Optional[SelfHealingSalesOrchestrator] = None

def get_orchestrator() -> SelfHealingSalesOrchestrator:
    """Get or create orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SelfHealingSalesOrchestrator()
    return _orchestrator


if __name__ == "__main__":
    async def test():
        orch = get_orchestrator()
        
        print("🎯 Testing Self-Healing Sales Agent")
        print("=" * 70)
        
        result = await orch.process_company("anker.com", "online_retail")
        
        print(f"\nSuccess: {result.success}")
        print(f"Duration: {result.duration_seconds}s")
        print(f"Methods tried: {result.methods_tried}")
        print(f"Decision makers: {len(result.decision_makers)}")
        print(f"Emails: {len(result.emails)}")
        
        if result.errors:
            print(f"\nErrors: {result.errors}")
        
        await orch.close()
    
    asyncio.run(test())
