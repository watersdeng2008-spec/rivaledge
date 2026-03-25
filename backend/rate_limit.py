"""
Shared rate limiter instance for RivalEdge.

Import `limiter` here to apply @limiter.limit() decorators in routers
without circular imports.
"""
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_user_or_ip_key(request: Request) -> str:
    """
    Rate-limit key: JWT sub for authenticated users, IP for everyone else.
    This is a best-effort parse — actual JWT validation still happens in auth.py.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        try:
            import base64
            import json as _json

            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload = _json.loads(base64.b64decode(payload_b64))
            sub = payload.get("sub")
            if sub:
                return f"user:{sub}"
        except Exception:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=get_user_or_ip_key)
