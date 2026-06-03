from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.config import settings
from app.db.supabase import get_supabase_admin_client
from app.repositories.profile_repository import ProfileRepository
from app.schemas.document import DocumentCategory
from app.schemas.profile import AppRole, ProfileResponse

MANAGER_ROLE_BY_CATEGORY: dict[DocumentCategory, set[AppRole]] = {
    DocumentCategory.hr: {AppRole.hr_admin, AppRole.admin},
    DocumentCategory.devops: {AppRole.devops_admin, AppRole.admin},
    DocumentCategory.security: {AppRole.security_admin, AppRole.admin},
    DocumentCategory.finance: {AppRole.finance_admin, AppRole.admin},
    DocumentCategory.technical: {AppRole.devops_admin, AppRole.admin},
    DocumentCategory.general: {
        AppRole.hr_admin,
        AppRole.devops_admin,
        AppRole.security_admin,
        AppRole.finance_admin,
        AppRole.admin,
    },
}


def get_profile_repository() -> ProfileRepository:
    return ProfileRepository(get_supabase_admin_client())


def parse_app_role(value: str | None) -> AppRole:
    if value is None:
        return AppRole.employee

    try:
        return AppRole(value)
    except ValueError:
        return AppRole.employee


def build_profile_from_record(record: dict) -> ProfileResponse:
    return ProfileResponse.model_validate(
        {
            **record,
            "role": parse_app_role(record.get("role")),
        }
    )


def build_development_profile() -> ProfileResponse:
    return ProfileResponse(
        id="00000000-0000-0000-0000-000000000001",
        email="devuser@example.com",
        full_name="Development Admin",
        avatar_url=None,
        role=AppRole.admin,
        department="Engineering",
        job_title="Local Developer",
        is_active=True,
    )


async def get_current_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileResponse:
    if (
        settings.app_env == "development"
        and current_user.id == "00000000-0000-0000-0000-000000000001"
    ):
        return build_development_profile()

    try:
        profile = profile_repository.ensure_exists(current_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User profile could not be loaded",
        ) from exc

    parsed_profile = build_profile_from_record(profile)

    if not parsed_profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return parsed_profile


def require_roles(*allowed_roles: AppRole) -> Callable:
    allowed = set(allowed_roles)

    async def dependency(
        profile: Annotated[ProfileResponse, Depends(get_current_profile)],
    ) -> ProfileResponse:
        if profile.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )

        return profile

    return dependency


require_admin = require_roles(AppRole.admin)


def can_manage_document_category(role: AppRole, category: DocumentCategory) -> bool:
    return role in MANAGER_ROLE_BY_CATEGORY[category]


def ensure_can_manage_document_category(
    role: AppRole,
    category: DocumentCategory,
) -> None:
    if not can_manage_document_category(role, category):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {role.value} cannot manage {category.value} documents",
        )
