import logging
import os
from inspect import signature
from typing import Protocol

logger = logging.getLogger(__name__)


class EmbeddingEncoder(Protocol):
    model_name: str

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class SentenceEmbeddingService:
    """Generates dense vectors using SentenceTransformers (runs locally on CPU/GPU)."""

    def __init__(self, model_name: str, hf_token: str | None = None) -> None:
        self.model_name = model_name
        self.hf_token = self._normalize_token(hf_token)
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model %s", self.model_name)
            if self.hf_token:
                os.environ["HF_TOKEN"] = self.hf_token
                os.environ["HUGGINGFACE_HUB_TOKEN"] = self.hf_token

            kwargs = {}
            if self.hf_token and "token" in signature(SentenceTransformer).parameters:
                kwargs["token"] = self.hf_token

            self._model = SentenceTransformer(self.model_name, **kwargs)
        return self._model

    @property
    def dimensions(self) -> int:
        return int(self._get_model().get_sentence_embedding_dimension())

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model = self._get_model()
        vectors = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [vector.tolist() for vector in vectors]

    @staticmethod
    def _normalize_token(value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().strip('"').strip("'")
        if not normalized or normalized.upper().startswith("YOUR_"):
            return None

        return normalized
