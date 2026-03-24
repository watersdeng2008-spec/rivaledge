"""
Pytest configuration and shared fixtures.
"""
import os
import sys

# Add backend to path so imports work without install
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Stub out required env vars for all tests
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-pem-key")
