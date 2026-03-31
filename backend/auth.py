"""
Clerk JWT validation middleware.

Uses JWKS URL for automatic key rotation — more reliable than
hardcoded PEM keys which can drift between dev/prod instances.
"""
import os
import time
from typing import Optional

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

# Cache the JWKS client to avoid fetching on every request
_jwks_client: Optional[PyJWKClient] = None
_jwks_client_created: float = 0
_JWKS_CACHE_TTL = 3600  # 1 hour


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client, _jwks_client_created
    now = time.time()
    if _jwks_client is None or (now - _jwks_client_created) > _JWKS_CACHE_TTL:
        issuer = os.environ.get("CLERK_JWT_ISSUER", "")
        if not issuer:
            raise RuntimeError("CLERK_JWT_ISSUER env var not set")
        jwks_url = f"{issuer}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
        _jwks_client_created = now
    return _jwks_client


def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT using JWKS URL for automatic key management.
    """
    issuer = os.environ.get("CLERK_JWT_ISSUER", "")
    
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer if issuer else None,
            options={"verify_aud": False},
        )
        return payload
    except Exception:
        # Fall back to PEM key if JWKS fails
        pem_key = os.environ.get("CLERK_PEM_PUBLIC_KEY", "").replace("\\n", "\n")
        if not pem_key:
            raise
        payload = jwt.decode(
            token,
            pem_key,
            algorithms=["RS256"],
            issuer=issuer if issuer else None,
            options={"verify_aud": False},
        )
        return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        payload = verify_clerk_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Auth error: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    if not credentials:
        return None
    try:
        return verify_clerk_token(credentials.credentials)
    except Exception:
        return None
