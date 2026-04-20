#!/usr/bin/env python3
"""Test Firecrawl API directly."""
import os
import httpx

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

def test_firecrawl():
    if not FIRECRAWL_API_KEY:
        print("❌ FIRECRAWL_API_KEY not set")
        return
    
    print(f"🔑 API Key present: {FIRECRAWL_API_KEY[:10]}...")
    
    # Test scrape
    url = "https://api.firecrawl.dev/v1/scrape"
    headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
    payload = {"url": "https://anker.com", "formats": ["markdown"]}
    
    print(f"\n🌐 Testing scrape: {payload['url']}")
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=60)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            if data.get('success'):
                content = data.get('data', {}).get('markdown', '')
                print(f"📄 Content length: {len(content)} chars")
                print(f"📝 Preview: {content[:500]}...")
            else:
                print(f"❌ Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_firecrawl()
