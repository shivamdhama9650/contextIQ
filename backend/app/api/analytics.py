from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.rbac import require_admin
from app.db.supabase import get_supabase_admin_client
from app.schemas.analytics import AnalyticsOverviewResponse
from app.schemas.profile import ProfileResponse
from app.services.analytics_service import (
    AnalyticsService,
    build_development_analytics_overview,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(get_supabase_admin_client())


@router.get("/admin/overview", response_model=AnalyticsOverviewResponse)
def get_admin_analytics_overview(
    _: Annotated[ProfileResponse, Depends(require_admin)],
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> AnalyticsOverviewResponse:
    try:
        return service.get_admin_overview()
    except Exception:
        if settings.app_env == "development":
            return build_development_analytics_overview()
        raise
