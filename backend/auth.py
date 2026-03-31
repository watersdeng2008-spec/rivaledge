"""
Clerk JWT validation middleware.

Validates Clerk JWTs using the PEM public key (CLERK_PEM_PUBLIC_KEY env var)
with JWKS URL as fallback for automatic key rotation.
"""
import os
import logging
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)
security = HTTPBearer()


def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT. Tries PEM key first, then JWKS URL as fallback.
    """
    issuer = os.environ.get("CLERK_JWT_ISSUER", "")

    # Method 1: PEM public key (fast, no network)
    pem_key = os.environ.get("CLERK_PEM_PUBLIC_KEY", "").replace("\\n", "\n")
    if pem_key:
        try:
            return jwt.decode(
                token,
                pem_key,
                algorithms=["RS256"],
                issuer=issuer or None,
                options={"verify_aud": False},
            )
        except jwt.InvalidTokenError as e:
            logger.debug("PEM verification failed: %s, trying JWKS", e)

    # Method 2: JWKS URL (network call, more reliable for key rotation)
    if issuer:
        try:
            from jwt import PyJWKClient
            jwks_url = f"{issuer}/.well-known/jwks.json"
            client = PyJWKClient(jwks_url, cache_keys=True, max_cached_keys=10)
            signing_key = client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=issuer,
                options={"verify_aud": False},
            )
        except Exception as e:
            logger.debug("JWKS verification failed: %s", e)
            raise jwt.InvalidTokenError(f"Token verification failed: {e}")

    raise jwt.InvalidTokenError("No valid verification method available")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        return verify_clerk_token(token)
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
