from pathlib import Path

from supabase import Client

from app.core.config import settings
from app.embeddings.sentence_embedding_service import SentenceEmbeddingService
from app.parsers.pdf_parser import PdfParserService
from app.repositories.chunk_embedding_repository import ChunkEmbeddingRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.storage_repository import StorageRepository
from app.services.document_chunking_service import DocumentChunkingService
from app.services.document_embedding_service import DocumentEmbeddingService
from app.services.document_parsing_service import DocumentParsingService
from app.services.document_vector_index_service import DocumentVectorIndexService
from app.services.rag_service import RAGService
from app.services.semantic_search_service import SemanticSearchService
from app.vector.chroma_store import ChromaVectorStore


def _chroma_store() -> ChromaVectorStore:
    persist_dir = str(Path(settings.chroma_persist_dir).resolve())
    return ChromaVectorStore(
        persist_directory=persist_dir,
        collection_name=settings.chroma_collection_name,
    )


def build_embedding_encoder() -> SentenceEmbeddingService:
    return SentenceEmbeddingService(
        settings.embedding_model_name,
        hf_token=settings.hf_token,
    )


def build_document_parsing_service(client: Client) -> DocumentParsingService:
    document_repository = DocumentRepository(client)
    document_page_repository = DocumentPageRepository(client)
    chunk_repository = DocumentChunkRepository(client)
    chunk_embedding_repository = ChunkEmbeddingRepository(client)

    embedding_encoder = build_embedding_encoder()
    embedding_service = DocumentEmbeddingService(
        document_chunk_repository=chunk_repository,
        chunk_embedding_repository=chunk_embedding_repository,
        embedding_encoder=embedding_encoder,
        batch_size=settings.embedding_batch_size,
    )
    vector_index_service = DocumentVectorIndexService(
        chroma_store=_chroma_store(),
        chunk_embedding_repository=chunk_embedding_repository,
        document_chunk_repository=chunk_repository,
        document_repository=document_repository,
    )

    return DocumentParsingService(
        document_repository=document_repository,
        document_page_repository=document_page_repository,
        storage_repository=StorageRepository(client),
        chunking_service=DocumentChunkingService(
            document_chunk_repository=chunk_repository,
        ),
        embedding_service=embedding_service,
        vector_index_service=vector_index_service,
        document_chunk_repository=chunk_repository,
        chunk_embedding_repository=chunk_embedding_repository,
        pdf_parser=PdfParserService(),
    )


def build_vector_index_service(client: Client) -> DocumentVectorIndexService:
    return DocumentVectorIndexService(
        chroma_store=_chroma_store(),
        chunk_embedding_repository=ChunkEmbeddingRepository(client),
        document_chunk_repository=DocumentChunkRepository(client),
        document_repository=DocumentRepository(client),
    )


def build_semantic_search_service() -> SemanticSearchService:
    return SemanticSearchService(
        chroma_store=_chroma_store(),
        embedding_encoder=build_embedding_encoder(),
    )


def build_rag_service() -> RAGService:
    from app.services.llm_factory import get_llm

    return RAGService(
        semantic_search_service=build_semantic_search_service(),
        llm=get_llm(),
    )
