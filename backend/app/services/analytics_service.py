from collections import Counter

from supabase import Client

from app.repositories.document_repository import DocumentRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.analytics import AnalyticsBreakdownItem, AnalyticsOverviewResponse
from app.schemas.document import DocumentResponse, DocumentStatus


class AnalyticsService:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.document_repository = DocumentRepository(client)
        self.profile_repository = ProfileRepository(client)

    def get_admin_overview(self) -> AnalyticsOverviewResponse:
        profiles = self.profile_repository.list_profiles()
        documents = self.document_repository.list_all(limit=250)

        total_documents = len(documents)
        status_counts = Counter(str(document.get("status", "unknown")) for document in documents)
        category_counts = Counter(
            str(document.get("category", "unknown")) for document in documents
        )
        role_counts = Counter(str(profile.get("role", "employee")) for profile in profiles)

        ready_documents = status_counts[DocumentStatus.ready.value]
        total_storage_bytes = sum(
            int(document.get("file_size_bytes") or 0) for document in documents
        )

        return AnalyticsOverviewResponse(
            total_users=len(profiles),
            active_users=sum(1 for profile in profiles if profile.get("is_active") is True),
            inactive_users=sum(1 for profile in profiles if profile.get("is_active") is False),
            total_documents=total_documents,
            ready_documents=ready_documents,
            failed_documents=status_counts[DocumentStatus.failed.value],
            processing_documents=status_counts[DocumentStatus.processing.value],
            uploaded_documents=status_counts[DocumentStatus.uploaded.value],
            archived_documents=status_counts[DocumentStatus.archived.value],
            total_storage_bytes=total_storage_bytes,
            total_chunks=self._count_table_rows("document_chunks"),
            total_embeddings=self._count_table_rows("chunk_embeddings"),
            readiness_rate=self._percentage(ready_documents, total_documents),
            category_breakdown=self._build_breakdown(category_counts, total_documents),
            status_breakdown=self._build_breakdown(status_counts, total_documents),
            role_breakdown=self._build_breakdown(role_counts, len(profiles)),
            recent_documents=[
                DocumentResponse.model_validate(document) for document in documents[:8]
            ],
        )

    def _count_table_rows(self, table_name: str) -> int:
        response = self.client.table(table_name).select("id", count="exact").execute()
        return response.count or 0

    def _build_breakdown(
        self,
        counts: Counter[str],
        total: int,
    ) -> list[AnalyticsBreakdownItem]:
        return [
            AnalyticsBreakdownItem(
                label=label,
                count=count,
                percentage=self._percentage(count, total),
            )
            for label, count in sorted(counts.items())
        ]

    def _percentage(self, value: int, total: int) -> float:
        if total == 0:
            return 0.0

        return round((value / total) * 100, 1)


def build_development_analytics_overview() -> AnalyticsOverviewResponse:
    return AnalyticsOverviewResponse(
        total_users=1,
        active_users=1,
        inactive_users=0,
        total_documents=0,
        ready_documents=0,
        failed_documents=0,
        processing_documents=0,
        uploaded_documents=0,
        archived_documents=0,
        total_storage_bytes=0,
        total_chunks=0,
        total_embeddings=0,
        readiness_rate=0,
        category_breakdown=[],
        status_breakdown=[],
        role_breakdown=[
            AnalyticsBreakdownItem(label="admin", count=1, percentage=100),
        ],
        recent_documents=[],
    )
