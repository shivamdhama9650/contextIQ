from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.analytics import get_analytics_service
from app.core.rbac import require_admin
from app.main import app
from app.schemas.analytics import AnalyticsBreakdownItem, AnalyticsOverviewResponse
from app.schemas.document import DocumentCategory, DocumentResponse, DocumentStatus
from app.schemas.profile import AppRole, ProfileResponse

client = TestClient(app)


class FakeAnalyticsService:
    def get_admin_overview(self) -> AnalyticsOverviewResponse:
        document = DocumentResponse(
            id="00000000-0000-0000-0000-000000000010",
            owner_id="00000000-0000-0000-0000-000000000001",
            title="Leave Policy",
            description=None,
            category=DocumentCategory.hr,
            storage_bucket="company-documents",
            storage_path="policies/leave.pdf",
            mime_type="application/pdf",
            file_size_bytes=1024,
            checksum_sha256=None,
            status=DocumentStatus.ready,
            error_message=None,
            uploaded_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return AnalyticsOverviewResponse(
            total_users=4,
            active_users=3,
            inactive_users=1,
            total_documents=2,
            ready_documents=1,
            failed_documents=1,
            processing_documents=0,
            uploaded_documents=0,
            archived_documents=0,
            total_storage_bytes=2048,
            total_chunks=12,
            total_embeddings=12,
            readiness_rate=50,
            category_breakdown=[
                AnalyticsBreakdownItem(label="hr", count=1, percentage=50),
                AnalyticsBreakdownItem(label="security", count=1, percentage=50),
            ],
            status_breakdown=[
                AnalyticsBreakdownItem(label="failed", count=1, percentage=50),
                AnalyticsBreakdownItem(label="ready", count=1, percentage=50),
            ],
            role_breakdown=[
                AnalyticsBreakdownItem(label="admin", count=1, percentage=25),
                AnalyticsBreakdownItem(label="employee", count=3, percentage=75),
            ],
            recent_documents=[document],
        )


def make_admin_profile() -> ProfileResponse:
    return ProfileResponse(
        id="00000000-0000-0000-0000-000000000001",
        email="admin@example.com",
        role=AppRole.admin,
        is_active=True,
    )


def test_admin_analytics_overview_returns_operational_metrics() -> None:
    app.dependency_overrides[require_admin] = make_admin_profile
    app.dependency_overrides[get_analytics_service] = FakeAnalyticsService

    try:
        response = client.get("/analytics/admin/overview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_users"] == 4
    assert payload["active_users"] == 3
    assert payload["ready_documents"] == 1
    assert payload["readiness_rate"] == 50
    assert payload["category_breakdown"][0]["label"] == "hr"
    assert payload["recent_documents"][0]["title"] == "Leave Policy"
