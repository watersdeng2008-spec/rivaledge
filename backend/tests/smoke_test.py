"""
Smoke test — run against live URL to verify deployment health.
Usage: SMOKE_URL=https://rivaledge-production.up.railway.app python smoke_test.py
"""
import httpx
import os

BASE_URL = os.environ.get("SMOKE_URL", "http://localhost:8000")

def test_endpoint(method, path, expected_statuses, **kwargs):
    try:
        r = getattr(httpx, method)(f"{BASE_URL}{path}", follow_redirects=True, timeout=10, **kwargs)
        passed = r.status_code in expected_statuses
        status = "✅" if passed else "❌"
        print(f"{status} {method.upper()} {path} → {r.status_code} (expected {expected_statuses})")
        return passed
    except Exception as e:
        print(f"❌ {method.upper()} {path} → ERROR: {e}")
        return False

if __name__ == "__main__":
    print(f"\n🔍 Running smoke tests against: {BASE_URL}\n")
    results = [
        test_endpoint("get",  "/health",             [200]),
        test_endpoint("post", "/api/users/me",       [401, 403], json={}),
        test_endpoint("post", "/api/competitors",    [401, 403], json={"url": "https://example.com"}),
        test_endpoint("get",  "/api/billing/status", [401, 403]),
    ]
    passed = sum(results)
    print(f"\n{'✅' if passed == len(results) else '⚠️ '} {passed}/{len(results)} smoke tests passed")
