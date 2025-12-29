"""Indexing pipeline for gist (Phase 2).

Pure-ish logic: walk -> extract -> hash/id -> embed -> store.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pathspec

from gist.embeddings import Embedder
from gist.extractor import detect_language, extract_code_blocks
from gist.store import StoredBlock, VectorStore
from gist.walker import iter_supported_files


@dataclass(frozen=True, slots=True)
class IndexStats:
    files_indexed: int
    blocks_extracted: int
    blocks_indexed: int


@dataclass(frozen=True, slots=True)
class _FileIndexStats:
    blocks_extracted: int
    blocks_indexed: int


def compute_content_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def compute_block_id(*, filename: str, start_line: int, end_line: int, content_hash: str) -> str:
    stable = f"{filename}:{start_line}:{end_line}:{content_hash}"
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _index_file(
    *,
    root: Path,
    file_path: Path,
    store: VectorStore,
    embedder: Embedder,
) -> _FileIndexStats | None:
    language = detect_language(file_path)
    if language is None:
        return None

    blocks = extract_code_blocks(file_path)
    rel_filename = file_path.relative_to(root).as_posix()

    stored_blocks: list[StoredBlock] = []
    for block in blocks:
        content_hash = compute_content_hash(block.code)
        block_id = compute_block_id(
            filename=rel_filename,
            start_line=block.start_line,
            end_line=block.end_line,
            content_hash=content_hash,
        )
        stored_blocks.append(
            StoredBlock(
                block_id=block_id,
                filename=rel_filename,
                start_line=block.start_line,
                end_line=block.end_line,
                parent_class=block.parent_class,
                language=language,
                content_hash=content_hash,
                code=block.code,
            )
        )

    if stored_blocks:
        embeddings = embedder.embed_texts([b.code for b in stored_blocks])
        store.upsert_blocks(stored_blocks, embeddings)

    return _FileIndexStats(blocks_extracted=len(blocks), blocks_indexed=len(stored_blocks))


def index_root(
    root: Path,
    *,
    store: VectorStore,
    embedder: Embedder,
    gitignore: pathspec.PathSpec,
    on_file_error: Callable[[Path, Exception], None] | None = None,
) -> IndexStats:
    root = root.resolve()

    files_indexed = 0
    blocks_extracted = 0
    blocks_indexed = 0

    for file_path in iter_supported_files(root, gitignore=gitignore):
        try:
            file_stats = _index_file(root=root, file_path=file_path, store=store, embedder=embedder)
        except Exception as exc:  # noqa: BLE001 - Phase 2: best-effort indexing  # pylint: disable=broad-exception-caught
            if on_file_error is not None:
                on_file_error(file_path, exc)
            continue

        if file_stats is None:
            continue

        files_indexed += 1
        blocks_extracted += file_stats.blocks_extracted
        blocks_indexed += file_stats.blocks_indexed

    return IndexStats(
        files_indexed=files_indexed,
        blocks_extracted=blocks_extracted,
        blocks_indexed=blocks_indexed,
    )
