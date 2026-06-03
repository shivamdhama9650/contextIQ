from pydantic import BaseModel


class SourceDetailResponse(BaseModel):
    """Schema returned by the `/api/source/{document_id}` endpoint.

    * ``document_id`` – the UUID of the document.
    * ``title`` – document title stored in the metadata table.
    * ``preview`` – first 500 characters of the document's first page (plain text).
    """

    document_id: str
    title: str
    preview: str
