"""Embedding layer for gist.

This module intentionally keeps the embedding interface small so tests can use a
stub embedder without downloading models.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

from sentence_transformers import SentenceTransformer


class Embedder(Protocol):
    """Protocol for embedding code blocks and queries."""

    @property
    def dimension(self) -> int:  # pragma: no cover
        ...

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_query(self, query: str) -> list[float]:
        ...


@dataclass(frozen=True, slots=True)
class SentenceTransformerEmbedder:
    """Embedder backed by `sentence-transformers`.

    Note: model download/caching is handled by the underlying libraries.
    """

    model_name: str = "all-MiniLM-L6-v2"

    @property
    def dimension(self) -> int:
        # The PRD and Phase 2 plan assume this model/dimension.
        return 384

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        model = _load_sentence_transformer(self.model_name)
        vectors = model.encode(list(texts), show_progress_bar=False)
        return [[float(x) for x in v.tolist()] for v in vectors]

    def embed_query(self, query: str) -> list[float]:
        model = _load_sentence_transformer(self.model_name)
        vector = model.encode([query], show_progress_bar=False)[0]
        return [float(x) for x in vector.tolist()]


@lru_cache(maxsize=4)
def _load_sentence_transformer(model_name: str) -> Any:
    return SentenceTransformer(model_name)


def get_default_embedder() -> Embedder:
    """Return the default embedder used by the CLI."""

    return SentenceTransformerEmbedder()
