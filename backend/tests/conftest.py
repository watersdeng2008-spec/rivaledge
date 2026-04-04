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
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("RESEND_API_KEY", "test-resend-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_fake")
os.environ.setdefault("STRIPE_SOLO_PRICE_ID", "price_1TEYfGLTMdu9rJFPT4iwohw9")
os.environ.setdefault("STRIPE_PRO_PRICE_ID", "price_1TEa3lLTMdu9rJFPgvechLBX")
