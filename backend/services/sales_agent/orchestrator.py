#!/usr/bin/env python3
"""
RivalEdge Sales Agent Orchestrator v2

Multi-industry templates with appropriate tone and focus:
- Online Retail / E-commerce: Platform tracking, customization, ROI
- Physical Therapy: Territory, partnerships, local market
"""

import os
import json
import asyncio
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, asdict

# API Keys from environment (strip whitespace to avoid header errors)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "").strip()
INSTANTLY_API_KEY = os.environ.get("INSTANTLY_API_KEY", "").strip()
HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY", "").strip()

DEFAULT_MODEL = "qwen/qwen-2.5-72b-instruct"


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
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class FirecrawlClient:
    """Client for Firecrawl web scraping API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"
    
    async def scrape(self, url: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/scrape",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url, "formats": ["markdown"]},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def search(self, query: str, limit: int = 5) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"query": query, "limit": limit},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()


class OpenRouterClient:
    """Client for OpenRouter LLM API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def complete(self, prompt: str, model: str = DEFAULT_MODEL) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://rivaledge.ai",
                    "X-Title": "RivalEdge Sales Agent"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class HunterClient:
    """Client for Hunter.io email finding."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
    
    async def find_email(self, domain: str, first_name: str, last_name: str) -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": self.api_key
                },
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and data["data"].get("email"):
                    return data["data"]
            return None
    
    async def domain_search(self, domain: str, limit: int = 10) -> List[Dict]:
        """Find all emails for a domain."""
        print(f"[Hunter] Searching domain: {domain}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/domain-search",
                params={
                    "domain": domain,
                    "limit": limit,
                    "api_key": self.api_key
                },
                timeout=30.0
            )
            print(f"[Hunter] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                print(f"[Hunter] Found {len(emails)} total emails for {domain}")
                
                if not emails:
                    return []
                
                # Filter for decision makers
                decision_maker_titles = [
                    "ceo", "founder", "chief", "vp", "vice president",
                    "head of", "director", "manager", "lead", "president",
                    "cco", "cmo", "cto", "cfo"
                ]
                filtered = []
                for email in emails:
                    position = (email.get("position") or "").lower()
                    if any(title in position for title in decision_maker_titles):
                        filtered.append(email)
                
                print(f"[Hunter] Filtered to {len(filtered)} decision makers for {domain}")
                
                # If no decision makers found, return first 3 emails anyway
                if not filtered and emails:
                    print(f"[Hunter] No decision makers found, returning first {min(3, len(emails))} emails")
                    return emails[:3]
                
                return filtered[:5]  # Top 5
            else:
                print(f"[Hunter] API error: {response.status_code} - {response.text[:200]}")
            return []


class EmailTemplateManager:
    """Manages industry-specific email templates."""
    
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
            "platforms": ["Amazon", "TikTok Shop", "Walmart", "Target", "DTC websites"],
            "tone": "Collaborative, assumes they're already trying, emphasizes consolidation"
        },
        
        "physical_therapy": {
            "name": "Physical Therapy / Healthcare",
            "subject": "New {{competitor_type}} activity near {{company_name}}",
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
            "focus_areas": ["New clinic openings", "Insurance networks", "Partnerships", "M&A"],
            "tone": "Territory-focused, emphasizes early warning, relationship-driven"
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
            "tone": "Direct, efficiency-focused"
        }
    }
    
    @classmethod
    def get_template(cls, industry: str) -> Dict:
        """Get template by industry key."""
        return cls.TEMPLATES.get(industry, cls.TEMPLATES["saas"])
    
    @classmethod
    def detect_industry(cls, company_data: Dict) -> str:
        """Detect industry from company data."""
        industry = company_data.get("industry", "").lower()
        products = company_data.get("products", "").lower()
        
        if any(word in industry or word in products for word in ["retail", "e-commerce", "amazon", "shopify", "dtc", "consumer goods"]):
            return "online_retail"
        elif any(word in industry or word in products for word in ["physical therapy", "healthcare", "medical", "pt ", "rehab"]):
            return "physical_therapy"
        else:
            return "saas"


class ResearchAgent:
    """Agent for researching leads and extracting personalization data."""
    
    def __init__(self, firecrawl: FirecrawlClient, openrouter: OpenRouterClient, hunter: HunterClient = None):
        self.firecrawl = firecrawl
        self.openrouter = openrouter
        self.hunter = hunter
    
    async def research_company(self, domain: str) -> Dict:
        """Research a company and extract key information."""
        scrape_result = await self.firecrawl.scrape(f"https://{domain}")
        
        if not scrape_result.get("success"):
            return {"error": "Failed to scrape website"}
        
        markdown = scrape_result["data"]["markdown"][:5000]
        
        prompt = f"""
Analyze this company website content and extract:
1. Industry/category
2. Main product/service
3. Target customers
4. Key competitors mentioned or implied
5. Positioning/how they describe themselves
6. Recent news or initiatives

Website content:
{markdown}

Return ONLY a JSON object with these fields:
- company_name (official name)
- industry (string)
- products (string, 1-2 sentences)
- target_customers (string)
- competitors (array of 3 main competitors)
- positioning (string, one sentence)
- recent_initiatives (array of strings, max 2)
"""
        
        try:
            response = await self.openrouter.complete(prompt)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            return {"error": "Could not parse LLM response"}
        except Exception as e:
            return {"error": str(e)}
    
    async def find_decision_makers(self, domain: str, company_name: str) -> List[Dict]:
        """Find decision-makers at the company using multiple methods."""
        print(f"[Research] Finding decision makers for {domain}")
        print(f"[Research] Hunter client available: {self.hunter is not None}")
        
        decision_makers = []
        
        # Method 1: Hunter.io domain search (most reliable)
        if self.hunter:
            try:
                hunter_emails = await self.hunter.domain_search(domain)
                if hunter_emails:
                    for email_data in hunter_emails[:3]:
                        first_name = email_data.get("first_name", "")
                        last_name = email_data.get("last_name", "")
                        position = email_data.get("position", "")
                        if first_name and position:
                            decision_makers.append({
                                "name": f"{first_name} {last_name}".strip(),
                                "title": position,
                                "relevance": f"{position} would care about competitive positioning",
                                "email": email_data.get("value", ""),
                                "source": "hunter.io"
                            })
                    if decision_makers:
                        return decision_makers
            except Exception as e:
                print(f"Hunter search failed: {e}")
        
        # Method 2: Try team/leadership pages
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
                    if any(title in content.lower() for title in ["ceo", "founder", "team", "leadership"]):
                        team_content += content[:3000] + "\n\n"
                        break
            except:
                continue
        
        # Method 3: Search for leadership if no team page
        if not team_content:
            try:
                search_result = await self.firecrawl.search(f"{company_name} CEO founder leadership team", limit=3)
                if search_result.get("success"):
                    for item in search_result.get("data", []):
                        team_content += item.get("markdown", "")[:2000] + "\n\n"
            except:
                pass
        
        # Method 4: Extract from content using LLM
        if team_content:
            prompt = f"""
Extract decision-makers from this company information.

Company: {company_name}
Content found:
{team_content[:4000]}

Identify 2-3 people who would be decision-makers for competitive intelligence software.
Look for: CEO, Founder, VP Product, Head of Strategy, Chief Strategy Officer, VP Marketing.

Return JSON array with objects containing:
- name (full name)
- title (exact job title)
- relevance (why they care about competitor monitoring, 1 sentence)
"""
            
            try:
                response = await self.openrouter.complete(prompt, max_tokens=800)
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                if json_start >= 0 and json_end > json_start:
                    return json.loads(response[json_start:json_end])
            except:
                pass
        
        # Fallback
        return [
            {"name": "CEO", "title": "Chief Executive Officer", "relevance": "Sets overall strategy", "source": "fallback"},
            {"name": "VP Product", "title": "VP Product", "relevance": "Manages product strategy", "source": "fallback"},
        ]


class PersonalizationAgent:
    """Agent for drafting personalized emails by industry."""
    
    def __init__(self, openrouter: OpenRouterClient):
        self.openrouter = openrouter
        self.templates = EmailTemplateManager()
    
    async def draft_email(self, lead: Lead, company_data: Dict, decision_maker: Dict, industry: str = None) -> Dict:
        """Draft a personalized email using industry-appropriate template."""
        
        # Detect industry if not provided
        if not industry:
            industry = self.templates.detect_industry(company_data)
        
        template = self.templates.get_template(industry)
        
        # Generate personalization hook based on industry
        if industry == "online_retail":
            hook = await self._generate_retail_hook(lead, company_data, decision_maker)
        elif industry == "physical_therapy":
            hook = await self._generate_pt_hook(lead, company_data, decision_maker)
        else:
            hook = await self._generate_saas_hook(lead, company_data, decision_maker)
        
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
            personalization_hook=hook
        )
        
        return {
            "subject": subject,
            "body": body,
            "industry": industry,
            "template_used": template["name"],
            "decision_maker": decision_maker,
            "platforms": template.get("platforms", []),
            "focus_areas": template.get("focus_areas", [])
        }
    
    async def _generate_retail_hook(self, lead: Lead, company_data: Dict, dm: Dict) -> str:
        """Generate hook for online retail."""
        prompt = f"""
Write one sentence about {lead.company_name} ({company_data.get('products', 'products')}) 
in the {company_data.get('industry', 'retail')} space.

Mention their market position or recent initiative. Keep it under 15 words.
Example: "leading the mobile charging market" or "expanding fast in sustainable home goods"

Return only the phrase, no punctuation at end.
"""
        try:
            hook = await self.openrouter.complete(prompt, max_tokens=100)
            return hook.strip().strip(".").strip(",")
        except:
            return f"growing fast in {company_data.get('industry', 'the market')}"
    
    async def _generate_pt_hook(self, lead: Lead, company_data: Dict, dm: Dict) -> str:
        """Generate hook for physical therapy."""
        prompt = f"""
Write one sentence about {lead.company_name} as a physical therapy practice.

Reference their positioning or a local market dynamic. Keep under 15 words.
Example: "growing fast in the Chicago metro area" or "known for sports rehab specialization"

Return only the phrase.
"""
        try:
            hook = await self.openrouter.complete(prompt, max_tokens=100)
            return hook.strip().strip(".")
        except:
            return "expanding in your market"
    
    async def _generate_saas_hook(self, lead: Lead, company_data: Dict, dm: Dict) -> str:
        """Generate hook for SaaS."""
        prompt = f"""
Write one sentence about {lead.company_name} ({company_data.get('products', 'SaaS')}).

Reference their positioning or competitive landscape. Keep under 15 words.

Return only the phrase.
"""
        try:
            hook = await self.openrouter.complete(prompt, max_tokens=100)
            return hook.strip().strip(".")
        except:
            return f"competing in {company_data.get('industry', 'SaaS')}"


class SalesAgentOrchestrator:
    """Main orchestrator for the sales agent system."""
    
    def __init__(self):
        self.firecrawl = FirecrawlClient(FIRECRAWL_API_KEY)
        self.openrouter = OpenRouterClient(OPENROUTER_API_KEY)
        self.hunter = HunterClient(HUNTER_API_KEY) if HUNTER_API_KEY else None
        self.research = ResearchAgent(self.firecrawl, self.openrouter, self.hunter)
        self.personalization = PersonalizationAgent(self.openrouter)
    
    async def process_company(self, domain: str, industry_hint: str = None) -> Dict:
        """Process a company through the full pipeline."""
        print(f"[Orchestrator] Processing {domain}")
        print(f"[Orchestrator] Hunter available: {self.hunter is not None}")
        print(f"[Orchestrator] ResearchAgent hunter: {self.research.hunter is not None}")
        
        results = {
            "domain": domain,
            "steps": [],
            "decision_makers": [],
            "emails": []
        }
        
        # Step 1: Research company
        try:
            company_data = await self.research.research_company(domain)
            results["company"] = company_data
            results["steps"].append({"research": "completed", "data": company_data})
        except Exception as e:
            print(f"[Orchestrator] Research failed: {e}")
            results["steps"].append({"research": "failed", "error": str(e)})
            return results
        
        # Step 2: Find decision-makers
        print(f"[Orchestrator] Calling find_decision_makers for {domain}")
        try:
            decision_makers = await self.research.find_decision_makers(domain, company_data.get("company_name", domain))
            print(f"[Orchestrator] Found {len(decision_makers)} decision makers")
            results["decision_makers"] = decision_makers
            results["steps"].append({"decision_makers": "completed", "count": len(decision_makers)})
        except Exception as e:
            print(f"[Orchestrator] find_decision_makers failed: {e}")
            results["steps"].append({"decision_makers": "failed", "error": str(e)})
            return results
        
        # Step 3: Draft emails for each decision-maker
        for dm in decision_makers[:2]:  # Top 2
            try:
                lead = Lead(
                    email="",  # Will fill with Hunter
                    first_name=dm.get("name", "").split()[0] if " " in dm.get("name", "") else dm.get("name", ""),
                    company_name=company_data.get("company_name", domain),
                    company_domain=domain
                )
                
                email = await self.personalization.draft_email(lead, company_data, dm, industry_hint)
                results["emails"].append(email)
            except Exception as e:
                results["steps"].append({"email_draft": "failed", "error": str(e)})
        
        results["steps"].append({"email_drafts": "completed", "count": len(results["emails"])})
        return results


# Singleton instance
_orchestrator: Optional[SalesAgentOrchestrator] = None

def get_orchestrator() -> SalesAgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SalesAgentOrchestrator()
    return _orchestrator


if __name__ == "__main__":
    async def test():
        orch = get_orchestrator()
        
        # Test online retail
        print("🎯 Testing Online Retail Template (Anker)")
        print("=" * 70)
        result = await orch.process_company("anker.com", "online_retail")
        
        if result["emails"]:
            email = result["emails"][0]
            print(f"\nIndustry: {email['industry']}")
            print(f"Template: {email['template_used']}")
            print(f"\nSubject: {email['subject']}")
            print(f"\nBody:\n{email['body']}")
        
        print("\n" + "=" * 70)
        
        # Test physical therapy
        print("\n🎯 Testing Physical Therapy Template")
        print("=" * 70)
        result = await orch.process_company("atipt.com", "physical_therapy")
        
        if result["emails"]:
            email = result["emails"][0]
            print(f"\nIndustry: {email['industry']}")
            print(f"Template: {email['template_used']}")
            print(f"\nSubject: {email['subject']}")
            print(f"\nBody:\n{email['body']}")
    
    asyncio.run(test())
