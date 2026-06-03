"""Helper script to create a test user and obtain a Supabase JWT.

Run from backend/ directory:
    python scripts/create_test_user.py
"""

from supabase import create_client

from app.core.config import settings


def main() -> None:
    if (
        not settings.supabase_url
        or not settings.supabase_anon_key
        or not settings.supabase_service_role_key
    ):
        print("ERROR: Supabase credentials not fully configured in backend/.env")
        return

    email = "shiva.test.user.assistant@gmail.com"
    password = "TestPassword123!"

    admin_client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    # 1. Delete existing user if present
    print(f"Checking for existing user: {email}")
    try:
        users_result = admin_client.auth.admin.list_users()
        # list_users returns an object with a 'users' attribute in newer versions of supabase-py
        users_list = getattr(users_result, "users", users_result)
        for user in users_list:
            if user.email == email:
                admin_client.auth.admin.delete_user(user.id)
                print(f"Deleted pre-existing user (ID: {user.id}) to ensure fresh configuration.")
                break
    except Exception as exc:
        print(f"Warning during user cleanup check: {exc}")

    # 2. Create and auto-confirm user
    print(f"Creating confirmed user: {email}")
    try:
        admin_client.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
            }
        )
        print("User created and auto-confirmed via Admin API.")
    except Exception as exc:
        print(f"Failed to create user: {exc}")
        return

    # 3. Use the public anon key to log in and get the JWT token
    anon_client = create_client(settings.supabase_url, settings.supabase_anon_key)
    try:
        response = anon_client.auth.sign_in_with_password({"email": email, "password": password})
        print("\n=== LOGIN SUCCESSFUL ===")
        print("Copy the JWT token below and paste it in the Swagger Authorize box:")
        print(f"\n{response.session.access_token}\n")
    except Exception as exc:
        print(f"\nFailed to log in: {exc}")


if __name__ == "__main__":
    main()
