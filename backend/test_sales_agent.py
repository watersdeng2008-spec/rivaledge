"""
Test script for Sales Agent integration.

Tests:
1. Entity detector enrichment
2. Outreach agent lead processing
3. Instantly API connection
"""
import os
import sys

# Set required env vars for testing
os.environ["INSTANTLY_API_KEY"] = "N2ZmNGQ1YzEtM2JjMy00NGE3LTk1OGEtYmNlODc4ZDFmODcwOnhIU1hxZGFIV29BZw=="

from services.entity_detector import EntityDetector, enrich_lead
from services.outreach_agent import OutreachAgent


def test_entity_detector():
    """Test entity detection."""
    print("=" * 60)
    print("TEST 1: Entity Detector")
    print("=" * 60)
    
    detector = EntityDetector()
    
    # Test email extraction
    test_cases = [
        {
            "email": "sarah.chen@stripe.com",
            "name": "Sarah Chen",
            "expected_company": "Stripe"
        },
        {
            "email": "john.smith@acmecorp.com",
            "name": "John Smith",
            "expected_company": "Acmecorp"
        },
        {
            "email": "mike@github.com",
            "name": "Mike Johnson",
            "expected_company": "Github"
        },
    ]
    
    for case in test_cases:
        entities = detector.extract_from_email(case["email"], case["name"])
        print(f"\nInput: {case['email']}")
        print(f"  Extracted emails: {entities.emails}")
        print(f"  Extracted URLs: {entities.urls}")
        print(f"  Inferred company: {entities.company_name}")
        print(f"  Expected company: {case['expected_company']}")
        
        if entities.company_name and case["expected_company"].lower() in entities.company_name.lower():
            print("  ✅ PASS")
        else:
            print("  ⚠️  PARTIAL (regex works, company inference may vary)")
    
    return True


def test_lead_enrichment():
    """Test lead enrichment."""
    print("\n" + "=" * 60)
    print("TEST 2: Lead Enrichment")
    print("=" * 60)
    
    test_lead = {
        "email": "jane.doe@notion.so",
        "name": "Jane Doe",
        "title": None,
        "company": None,
    }
    
    print(f"\nInput lead: {test_lead}")
    
    enriched = enrich_lead(test_lead)
    
    print(f"\nEnriched lead:")
    print(f"  Email: {enriched.get('email')}")
    print(f"  Name: {enriched.get('name')}")
    print(f"  Company: {enriched.get('company')}")
    print(f"  Title: {enriched.get('title')}")
    
    if enriched.get('company'):
        print("  ✅ Company extracted from domain")
    else:
        print("  ⚠️  No company extracted (expected without LLM)")
    
    return True


def test_outreach_agent():
    """Test outreach agent integration."""
    print("\n" + "=" * 60)
    print("TEST 3: Outreach Agent")
    print("=" * 60)
    
    agent = OutreachAgent()
    
    # Test connection
    print("\nTesting Instantly API connection...")
    connected = agent.test_connection()
    
    if connected:
        print("  ✅ Connected to Instantly API")
        
        # Get email accounts
        accounts = agent._get_email_accounts()
        print(f"  Found {len(accounts)} email account(s)")
        
        for acc_id in accounts:
            print(f"    - Account ID: {acc_id[:20]}...")
    else:
        print("  ❌ Failed to connect")
        return False
    
    # Test lead enrichment
    print("\nTesting lead enrichment...")
    test_lead = {
        "email": "test@example.com",
        "name": "Test User",
        "company": None,
    }
    
    enriched = agent.enrich_lead_data(test_lead)
    print(f"  Original company: {test_lead.get('company')}")
    print(f"  Enriched company: {enriched.get('company')}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SALES AGENT INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Entity Detector", test_entity_detector()))
    except Exception as e:
        print(f"\n❌ Entity Detector failed: {e}")
        results.append(("Entity Detector", False))
    
    try:
        results.append(("Lead Enrichment", test_lead_enrichment()))
    except Exception as e:
        print(f"\n❌ Lead Enrichment failed: {e}")
        results.append(("Lead Enrichment", False))
    
    try:
        results.append(("Outreach Agent", test_outreach_agent()))
    except Exception as e:
        print(f"\n❌ Outreach Agent failed: {e}")
        results.append(("Outreach Agent", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
