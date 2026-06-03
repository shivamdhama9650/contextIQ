import logging

from fastapi import HTTPException, status
from storage3.exceptions import StorageApiError
from supabase import Client

logger = logging.getLogger(__name__)


class StorageRepository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def upload_pdf(self, bucket: str, path: str, content: bytes) -> None:
        try:
            self.client.storage.from_(bucket).upload(
                path,
                content,
                file_options={
                    "content-type": "application/pdf",
                    "cache-control": "3600",
                    "upsert": "false",
                },
            )
        except StorageApiError as exc:
            logger.exception("Storage upload failed for path %s", path)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to store document: {exc}",
            ) from exc

    def download_pdf(self, bucket: str, path: str) -> bytes:
        try:
            return self.client.storage.from_(bucket).download(path)
        except StorageApiError as exc:
            logger.exception("Storage download failed for path %s", path)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to download document: {exc}",
            ) from exc

    def delete_pdf(self, bucket: str, path: str) -> None:
        try:
            self.client.storage.from_(bucket).remove([path])
        except StorageApiError:
            logger.exception("Failed to delete orphaned storage object at %s", path)
