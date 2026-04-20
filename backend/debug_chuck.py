#!/usr/bin/env python3
"""
Debug script for Chuck Clark's account.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.supabase import get_competitors

def debug_chuck():
    chuck_email = "charles.clark.0628@gmail.com"
    print(f"🔍 Checking Chuck's account: {chuck_email}")
    
    # Need to find user_id first
    import httpx
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    
    # Find user
    url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{chuck_email}&limit=1"
    r = httpx.get(url, headers=headers, timeout=10)
    users = r.json()
    
    if not users:
        print(f"❌ User not found: {chuck_email}")
        return
    
    user = users[0]
    user_id = user["id"]
    
    print(f"✅ User: {user['email']}")
    print(f"   ID: {user_id}")
    print(f"   Plan: {user.get('plan', 'unknown')}")
    
    # Get competitors
    comps = get_competitors(user_id)
    print(f"\n📊 Competitors: {len(comps)}")
    for c in comps:
        print(f"   - {c.get('name', 'Unnamed')}: {c.get('url', 'no URL')}")
    
    # Check API keys
    print(f"\n🔑 API Keys:")
    print(f"   OPENROUTER: {'✅' if os.environ.get('OPENROUTER_API_KEY') else '❌'}")
    print(f"   BRAVE: {'✅' if os.environ.get('BRAVE_SEARCH_API_KEY') else '❌'}")

if __name__ == "__main__":
    debug_chuck()
