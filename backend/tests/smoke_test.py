"""
RivalEdge Smoke Test
Usage: SMOKE_URL=https://your-railway-url.railway.app python smoke_test.py

Tests basic endpoint availability and auth enforcement against a live deployment.
This is NOT a pytest test — run it directly with Python.
"""
import httpx
import os
import sys

BASE_URL = os.environ.get("SMOKE_URL", "http://localhost:8000")


def check_endpoint(method: str, path: str, expected_status: int, **kwargs) -> bool:
    """Hit an endpoint and verify the expected HTTP status code."""
    url = f"{BASE_URL}{path}"
    try:
        r = getattr(httpx, method)(url, timeout=10.0, **kwargs)
        ok = r.status_code == expected_status
        icon = "✅" if ok else "❌"
        print(f"{icon} {method.upper()} {path} → {r.status_code} (expected {expected_status})")
        if not ok:
            try:
                print(f"   Response: {r.text[:200]}")
            except Exception:
                pass
        return ok
    except httpx.RequestError as exc:
        print(f"❌ {method.upper()} {path} → CONNECTION ERROR: {exc}")
        return False


def run() -> bool:
    print(f"\n🔍 Running smoke tests against: {BASE_URL}\n")

    results = [
        check_endpoint("get", "/health", 200),
        check_endpoint("post", "/api/users/me", 401, json={}),
        check_endpoint("post", "/api/competitors", 401, json={"url": "https://example.com"}),
        check_endpoint("get", "/api/billing/status", 401),
    ]

    passed = sum(results)
    total = len(results)
    print(f"\n{'✅' if passed == total else '⚠️ '} {passed}/{total} smoke tests passed\n")
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
