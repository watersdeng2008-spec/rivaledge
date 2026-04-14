#!/usr/bin/env python3
"""
Self-Healing Sales Agent Cron Job v2

Features:
- Automatic retries and fallbacks
- Detailed logging and diagnostics
- Performance tracking
- Self-healing capabilities
"""
import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sales_agent.self_healing_orchestrator import get_orchestrator, ResearchResult

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# Target companies - expanded list
TARGETS = [
    # Online Retail / E-commerce (high priority)
    {"domain": "anker.com", "industry": "online_retail", "priority": 1},
    {"domain": "belkin.com", "industry": "online_retail", "priority": 1},
    {"domain": "ravpower.com", "industry": "online_retail", "priority": 2},
    {"domain": "aukey.com", "industry": "online_retail", "priority": 2},
    {"domain": "mophie.com", "industry": "online_retail", "priority": 2},
    {"domain": "nonda.co", "industry": "online_retail", "priority": 3},
    {"domain": "zendure.com", "industry": "online_retail", "priority": 3},
    {"domain": "ugreen.com", "industry": "online_retail", "priority": 3},
    {"domain": "baseus.com", "industry": "online_retail", "priority": 3},
    {"domain": "spigen.com", "industry": "online_retail", "priority": 3},
    
    # SaaS / Software
    {"domain": "notion.so", "industry": "saas", "priority": 2},
    {"domain": "figma.com", "industry": "saas", "priority": 2},
    {"domain": "linear.app", "industry": "saas", "priority": 3},
    {"domain": "raycast.com", "industry": "saas", "priority": 3},
    {"domain": "loom.com", "industry": "saas", "priority": 3},
    
    # Physical Therapy
    {"domain": "ivyrehab.com", "industry": "physical_therapy", "priority": 3},
    {"domain": "athletico.com", "industry": "physical_therapy", "priority": 3},
]


def log_to_supabase(data: Dict) -> bool:
    """Log results to Supabase with error handling."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  Supabase credentials not set")
        return False
    
    try:
        import httpx
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        
        url = f"{SUPABASE_URL}/rest/v1/sales_agent_logs"
        response = httpx.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 201:
            print(f"✅ Logged to Supabase: {data.get('run_id')}")
            return True
        else:
            print(f"⚠️  Failed to log: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"⚠️  Error logging to Supabase: {e}")
        return False


def save_leads_to_supabase(leads: List[Dict], run_id: str) -> bool:
    """Save individual leads to database."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    
    try:
        import httpx
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        
        url = f"{SUPABASE_URL}/rest/v1/sales_leads"
        
        for lead in leads:
            lead["run_id"] = run_id
            try:
                httpx.post(url, json=lead, headers=headers, timeout=10)
            except Exception as e:
                print(f"⚠️  Failed to save lead: {e}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error saving leads: {e}")
        return False


async def run_daily_sales_agent(target_count: int = 10) -> Dict:
    """Run sales agent with full diagnostics."""
    run_id = datetime.now(timezone.utc).isoformat()
    print(f"\n{'='*70}")
    print(f"🚀 Self-Healing Sales Agent v2 - Run: {run_id}")
    print(f"{'='*70}")
    print(f"📊 Target count: {target_count}")
    print(f"🤖 Using free Qwen tokens for cost efficiency\n")
    
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
        "successful_researches": 0,
        "failed_researches": 0,
        "total_duration_seconds": 0,
        "errors": [],
        "details": [],
        "all_methods_tried": set(),
    }
    
    all_leads = []
    
    for i, target in enumerate(sorted_targets, 1):
        domain = target["domain"]
        industry = target["industry"]
        
        print(f"\n[{i}/{len(sorted_targets)}] 🔍 Processing: {domain} ({industry})")
        print("-" * 50)
        
        try:
            # Run research with self-healing orchestrator
            result: ResearchResult = await orchestrator.process_company(domain, industry)
            
            # Update stats
            results["companies_processed"] += 1
            results["decision_makers_found"] += len(result.decision_makers)
            results["emails_generated"] += len(result.emails)
            results["total_duration_seconds"] += result.duration_seconds
            results["all_methods_tried"].update(result.methods_tried)
            
            if result.success:
                results["successful_researches"] += 1
                print(f"  ✅ SUCCESS in {result.duration_seconds:.1f}s")
                print(f"     Decision makers: {len(result.decision_makers)}")
                print(f"     Emails generated: {len(result.emails)}")
                print(f"     Methods: {', '.join(result.methods_tried)}")
            else:
                results["failed_researches"] += 1
                print(f"  ⚠️  PARTIAL in {result.duration_seconds:.1f}s")
                print(f"     Issues: {result.errors}")
            
            # Prepare leads for database
            for email_data in result.emails:
                lead_record = {
                    "domain": domain,
                    "industry": industry,
                    "company_name": result.company_data.get("company_name", domain),
                    "decision_maker_name": email_data.get("decision_maker", {}).get("name", ""),
                    "decision_maker_title": email_data.get("decision_maker", {}).get("title", ""),
                    "email": "",  # To be filled by Hunter
                    "email_subject": email_data.get("subject", ""),
                    "email_body": email_data.get("body", ""),
                    "template_used": email_data.get("template_used", ""),
                    "personalization_method": email_data.get("personalization_method", ""),
                    "source": "sales_agent_v2",
                    "status": "new",
                }
                all_leads.append(lead_record)
            
            results["details"].append({
                "domain": domain,
                "industry": industry,
                "success": result.success,
                "duration": result.duration_seconds,
                "decision_makers": len(result.decision_makers),
                "emails": len(result.emails),
                "methods": result.methods_tried,
                "errors": result.errors,
            })
            
        except Exception as e:
            error_msg = f"Critical failure on {domain}: {str(e)}"
            print(f"  ❌ {error_msg}")
            results["errors"].append(error_msg)
            results["failed_researches"] += 1
            results["details"].append({
                "domain": domain,
                "industry": industry,
                "success": False,
                "error": str(e),
            })
    
    # Finalize results
    results["completed_at"] = datetime.now(timezone.utc).isoformat()
    results["all_methods_tried"] = list(results["all_methods_tried"])
    
    # Calculate averages
    if results["companies_processed"] > 0:
        results["avg_duration_per_company"] = round(
            results["total_duration_seconds"] / results["companies_processed"], 2
        )
    
    # Print summary
    print(f"\n{'='*70}")
    print("📈 RUN SUMMARY")
    print(f"{'='*70}")
    print(f"  Companies processed: {results['companies_processed']}")
    print(f"  Successful: {results['successful_researches']}")
    print(f"  Failed: {results['failed_researches']}")
    print(f"  Decision makers found: {results['decision_makers_found']}")
    print(f"  Emails generated: {results['emails_generated']}")
    print(f"  Total duration: {results['total_duration_seconds']:.1f}s")
    print(f"  Avg per company: {results.get('avg_duration_per_company', 0):.1f}s")
    print(f"  Methods used: {', '.join(results['all_methods_tried'])}")
    
    if results["errors"]:
        print(f"\n  Errors ({len(results['errors'])}):")
        for err in results["errors"][:5]:
            print(f"    - {err}")
    
    # Log to Supabase
    print(f"\n💾 Saving to database...")
    log_success = log_to_supabase(results)
    if log_success and all_leads:
        save_leads_to_supabase(all_leads, run_id)
    
    # Cleanup
    await orchestrator.close()
    
    print(f"\n✅ Run complete: {run_id}")
    print(f"{'='*70}\n")
    
    return results


if __name__ == "__main__":
    # Get target count from args
    target_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # Run
    asyncio.run(run_daily_sales_agent(target_count))
