from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError
from pydantic import BaseModel

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    id: str
    email: str | None = None
    role: str | None = None
    claims: dict[str, Any]


def _get_jwks_url() -> str:
    if not settings.supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is not configured",
        )

    return f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"


def _verify_access_token(token: str) -> dict[str, Any]:
    try:
        jwks_client = PyJWKClient(_get_jwks_url())
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedUser:
    if credentials is not None and credentials.scheme.lower() == "bearer":
        claims = _verify_access_token(credentials.credentials)
        user_id = claims.get("sub")

        if not isinstance(user_id, str) or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing a subject",
            )

        email = claims.get("email")
        role = claims.get("role")

        return AuthenticatedUser(
            id=user_id,
            email=email if isinstance(email, str) else None,
            role=role if isinstance(role, str) else None,
            claims=claims,
        )

    # Developer Auto-Bypass: allow local API testing without a browser session.
    # Real browser sessions still use the Supabase JWT path above.
    if settings.app_env == "development":
        return AuthenticatedUser(
            id="00000000-0000-0000-0000-000000000001",
            email="devuser@example.com",
            role="admin",
            claims={
                "sub": "00000000-0000-0000-0000-000000000001",
                "email": "devuser@example.com",
                "role": "admin",
            },
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing bearer token",
    )
