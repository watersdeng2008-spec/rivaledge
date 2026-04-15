#!/usr/bin/env python3
"""
Daily Sales Agent Cron Job

Runs at 9:00 AM CST daily to:
1. Research new companies
2. Generate personalized emails
3. Add leads to Instantly campaign
4. Log results for performance tracking
"""
import os
import sys
import json
import httpx
from datetime import datetime, timezone
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sales_agent.orchestrator import get_orchestrator

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
INSTANTLY_API_KEY = os.environ.get("INSTANTLY_API_KEY", "")
INSTANTLY_CAMPAIGN_ID = "a0b77cca-5750-4048-a5f2-98c05fecce0f"  # RivalEdge Outreach

# Target companies by priority
TARGETS = [
    # SaaS / Software (better team pages)
    {"domain": "notion.so", "industry": "saas", "priority": 1},
    {"domain": "figma.com", "industry": "saas", "priority": 1},
    {"domain": "linear.app", "industry": "saas", "priority": 2},
    {"domain": "raycast.com", "industry": "saas", "priority": 2},
    {"domain": "loom.com", "industry": "saas", "priority": 2},
    {"domain": "cal.com", "industry": "saas", "priority": 2},
    {"domain": "vercel.com", "industry": "saas", "priority": 2},
    {"domain": "supabase.com", "industry": "saas", "priority": 2},
    
    # Online Retail / E-commerce
    {"domain": "anker.com", "industry": "online_retail", "priority": 3},
    {"domain": "belkin.com", "industry": "online_retail", "priority": 3},
    {"domain": "ravpower.com", "industry": "online_retail", "priority": 3},
    {"domain": "aukey.com", "industry": "online_retail", "priority": 3},
    {"domain": "mophie.com", "industry": "online_retail", "priority": 3},
    {"domain": "nonda.co", "industry": "online_retail", "priority": 3},
    {"domain": "zendure.com", "industry": "online_retail", "priority": 3},
    {"domain": "ugreen.com", "industry": "online_retail", "priority": 3},
    {"domain": "baseus.com", "industry": "online_retail", "priority": 3},
    {"domain": "spigen.com", "industry": "online_retail", "priority": 3},
    
    # Physical Therapy (experimental - Chuck's market)
    {"domain": "atipt.com", "industry": "physical_therapy", "priority": 3, "note": "Chuck's company - skip"},
    {"domain": "ivyrehab.com", "industry": "physical_therapy", "priority": 3},
    {"domain": "athletico.com", "industry": "physical_therapy", "priority": 3},
]


def log_to_supabase(data: Dict):
    """Log sales agent run to database for tracking."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase credentials not set, skipping logging")
        return
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    
    url = f"{SUPABASE_URL}/rest/v1/sales_agent_logs"
    
    try:
        response = httpx.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 201:
            print(f"✅ Logged to Supabase: {data.get('run_id')}")
        else:
            print(f"⚠️ Failed to log: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"⚠️ Error logging to Supabase: {e}")


def add_to_instantly(email: str, first_name: str, company: str, title: str, 
                     personalized_subject: str, personalized_body: str) -> bool:
    """Add lead to Instantly campaign."""
    if not INSTANTLY_API_KEY:
        print("⚠️ Instantly API key not set")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {INSTANTLY_API_KEY}",
            "Content-Type": "application/json",
        }
        
        # Instantly API v2 expects personalization as custom fields, not nested object
        # Store the personalized content in custom fields
        payload = {
            "campaign_id": INSTANTLY_CAMPAIGN_ID,
            "email": email,
            "first_name": first_name,
            "last_name": "",
            "company_name": company,
            "title": title,
            # Custom variables for email templates - these become {{variable}} in Instantly
            "custom_variables": {
                "personalized_subject": personalized_subject,
                "personalized_body": personalized_body,
            }
        }
        
        response = httpx.post(
            "https://api.instantly.ai/api/v2/leads",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Added to Instantly: {email}")
            return True
        else:
            print(f"⚠️ Failed to add to Instantly: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error adding to Instantly: {e}")
        return False


async def run_daily_sales_agent(target_count: int = 3):
    """
    Run sales agent daily.
    
    Args:
        target_count: Number of companies to research (default 3 to avoid rate limits)
    """
    run_id = datetime.now(timezone.utc).isoformat()
    print(f"🚀 Starting Sales Agent Run: {run_id}")
    print(f"📊 Target count: {target_count}")
    
    orchestrator = get_orchestrator()
    
    # Sort by priority and take top targets
    sorted_targets = sorted(TARGETS, key=lambda x: x["priority"])[:target_count]
    
    results = {
        "run_id": run_id,
        "started_at": run_id,
        "target_count": target_count,
        "companies_processed": 0,
        "decision_makers_found": 0,
        "emails_generated": 0,
        "emails_added_to_instantly": 0,
        "errors": [],
        "details": [],
    }
    
    for target in sorted_targets:
        domain = target["domain"]
        industry = target["industry"]
        
        print(f"\n🔍 Processing: {domain} ({industry})")
        
        try:
            # Research company
            result = await orchestrator.process_company(domain, industry)
            
            companies_processed = 1
            decision_makers = len(result.get("decision_makers", []))
            emails = len(result.get("emails", []))
            
            results["companies_processed"] += companies_processed
            results["decision_makers_found"] += decision_makers
            results["emails_generated"] += emails
            
            detail = {
                "domain": domain,
                "industry": industry,
                "status": "success",
                "decision_makers": decision_makers,
                "emails": emails,
            }
            
            # Add to Instantly if we have emails with actual email addresses
            for email_data in result.get("emails", []):
                dm = email_data.get('decision_maker', {})
                email_address = dm.get('email', '')
                first_name = dm.get('name', '').split()[0] if dm.get('name') else ''
                company = result.get('company', {}).get('company_name', domain)
                title = dm.get('title', '')
                
                if email_address:
                    success = add_to_instantly(
                        email=email_address,
                        first_name=first_name,
                        company=company,
                        title=title,
                        personalized_subject=email_data.get('subject', ''),
                        personalized_body=email_data.get('body', '')
                    )
                    if success:
                        results["emails_added_to_instantly"] += 1
                else:
                    print(f"  📧 Generated email for: {dm.get('name', 'Unknown')} (no email - manual research needed)")
            
            results["details"].append(detail)
            print(f"  ✅ Found {decision_makers} decision makers, {emails} emails")
            
        except Exception as e:
            error_msg = f"Failed to process {domain}: {str(e)}"
            print(f"  ❌ {error_msg}")
            results["errors"].append(error_msg)
            results["details"].append({
                "domain": domain,
                "industry": industry,
                "status": "error",
                "error": str(e),
            })
    
    # Finalize
    results["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Log to Supabase
    log_to_supabase(results)
    
    # Print summary
    print(f"\n📈 Sales Agent Run Complete: {run_id}")
    print(f"   Companies: {results['companies_processed']}")
    print(f"   Decision Makers: {results['decision_makers_found']}")
    print(f"   Emails Generated: {results['emails_generated']}")
    print(f"   Errors: {len(results['errors'])}")
    
    return results


if __name__ == "__main__":
    import asyncio
    
    # Get target count from args or default to 3
    target_count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    
    # Run
    asyncio.run(run_daily_sales_agent(target_count))
