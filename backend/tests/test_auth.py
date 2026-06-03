from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# NOTE: In development mode (APP_ENV=development), the backend auto-authenticates
# requests using a fixed dev user. This is intentional for local testing convenience.
# In production (APP_ENV=production), all endpoints require a valid Supabase JWT.


def test_dev_bypass_auto_authenticates() -> None:
    """In dev mode, requests without a token should be auto-authenticated."""
    response = client.get("/auth/me")
    # The dev bypass auto-logs in; /auth/me tries to load a profile from DB.
    # It will either return 200 (if profile exists) or 500 (DB unreachable in CI).
    # What it must NOT return is 401 (Unauthorized), because the bypass is active.
    assert response.status_code != 401


def test_dev_bypass_user_has_valid_uuid() -> None:
    """Dev bypass user ID must be a valid UUID (required by PostgreSQL UUID columns)."""
    import asyncio

    from app.core.auth import get_current_user

    user = asyncio.run(get_current_user(credentials=None))
    assert user.id == "00000000-0000-0000-0000-000000000001"
    assert user.email == "devuser@example.com"
    assert user.role == "admin"
