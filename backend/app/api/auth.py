from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.rbac import (
    build_development_profile,
    get_current_profile,
    get_profile_repository,
    require_admin,
)
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileRoleUpdateRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=ProfileResponse)
async def read_current_user(
    profile: Annotated[ProfileResponse, Depends(get_current_profile)],
) -> ProfileResponse:
    return profile


@router.get("/profiles", response_model=list[ProfileResponse])
def list_profiles(
    _: Annotated[ProfileResponse, Depends(require_admin)],
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> list[ProfileResponse]:
    try:
        return [
            ProfileResponse.model_validate(profile)
            for profile in profile_repository.list_profiles()
        ]
    except Exception:
        if settings.app_env == "development":
            return [build_development_profile()]
        raise


@router.patch("/profiles/{user_id}/role", response_model=ProfileResponse)
def update_profile_role(
    user_id: str,
    payload: ProfileRoleUpdateRequest,
    _: Annotated[ProfileResponse, Depends(require_admin)],
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileResponse:
    try:
        updated_profile = profile_repository.update_role(
            user_id=user_id,
            role=payload.role.value,
        )
        return ProfileResponse.model_validate(updated_profile)
    except Exception:
        if (
            settings.app_env == "development"
            and user_id == "00000000-0000-0000-0000-000000000001"
        ):
            profile = build_development_profile()
            return profile.model_copy(update={"role": payload.role})
        raise
