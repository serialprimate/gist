"""Vector store persistence for gist.

Encapsulates ChromaDB persistence under `.gist/chroma/` and provides the
minimal operations needed by the CLI.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, TypedDict, cast

import chromadb


class CodeBlockMetadata(TypedDict):
    filename: str
    start_line: int
    end_line: int
    parent_class: str | None
    language: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class StoredBlock:
    block_id: str
    filename: str
    start_line: int
    end_line: int
    parent_class: str | None
    language: str
    content_hash: str
    code: str


@dataclass(frozen=True, slots=True)
class SearchHit:
    block_id: str
    filename: str
    start_line: int
    end_line: int
    parent_class: str | None
    language: str
    content_hash: str
    code: str
    distance: float | None


def chroma_dir(root: Path) -> Path:
    return root / ".gist" / "chroma"


class _ChromaCollection(Protocol):
    def upsert(
        self,
        *,
        ids: list[str],
        documents: list[str],
        metadatas: list[CodeBlockMetadata],
        embeddings: list[list[float]],
    ) -> Any:
        ...

    def query(
        self, *, query_embeddings: list[list[float]], n_results: int
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class VectorStore:
    root: Path
    _collection: _ChromaCollection

    def upsert_blocks(
        self, blocks: Sequence[StoredBlock], embeddings: Sequence[Sequence[float]]
    ) -> None:
        if len(blocks) != len(embeddings):
            raise ValueError("blocks and embeddings length mismatch")

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[CodeBlockMetadata] = []
        vectors: list[list[float]] = []

        for block, embedding in zip(blocks, embeddings, strict=True):
            ids.append(block.block_id)
            documents.append(block.code)
            metadatas.append(
                {
                    "filename": block.filename,
                    "start_line": block.start_line,
                    "end_line": block.end_line,
                    "parent_class": block.parent_class,
                    "language": block.language,
                    "content_hash": block.content_hash,
                }
            )
            vectors.append(list(embedding))

        collection = self._collection
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=vectors)

    def query(self, embedding: Sequence[float], *, top_k: int = 3) -> list[SearchHit]:
        if top_k <= 0:
            raise ValueError("top_k must be > 0")

        collection = self._collection
        result: dict[str, Any] = collection.query(
            query_embeddings=[list(embedding)], n_results=top_k
        )

        ids_nested: list[list[str]] = result.get("ids", [[]])
        docs_nested: list[list[str]] = result.get("documents", [[]])
        metas_nested: list[list[CodeBlockMetadata]] = result.get("metadatas", [[]])
        dists_nested: list[list[float]] | None = result.get("distances")

        ids = ids_nested[0] if ids_nested else []
        docs = docs_nested[0] if docs_nested else []
        metas = metas_nested[0] if metas_nested else []
        dists = (dists_nested[0] if dists_nested else None) if dists_nested is not None else None

        hits: list[SearchHit] = []

        count = min(len(ids), len(docs), len(metas))
        for idx in range(count):
            block_id = ids[idx]
            code = docs[idx]
            meta = metas[idx]
            distance = dists[idx] if dists is not None and idx < len(dists) else None
            hits.append(
                SearchHit(
                    block_id=block_id,
                    filename=meta["filename"],
                    start_line=int(meta["start_line"]),
                    end_line=int(meta["end_line"]),
                    parent_class=meta.get("parent_class"),
                    language=meta["language"],
                    content_hash=meta["content_hash"],
                    code=code,
                    distance=distance,
                )
            )
        return hits


def open_store(root: Path) -> VectorStore:  # pylint: disable=unused-variable
    """Open (or create) a persistent ChromaDB store under ROOT."""

    root = root.resolve()
    persist_dir = chroma_dir(root)
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(name="code", metadata={"hnsw:space": "cosine"})
    return VectorStore(root=root, _collection=cast(_ChromaCollection, collection))
