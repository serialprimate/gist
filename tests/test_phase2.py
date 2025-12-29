from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pathspec

from gist.embeddings import Embedder
from gist.indexer import compute_block_id, compute_content_hash, index_root
from gist.store import StoredBlock, VectorStore, open_store


class _StubEmbedder:
    @property
    def dimension(self) -> int:
        return 1

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t))] for t in texts]

    def embed_query(self, query: str) -> list[float]:
        return [float(len(query))]


def test_store_roundtrip_single_block(tmp_path: Path) -> None:  # pylint: disable=unused-variable
    root = tmp_path
    store = open_store(root)

    block = StoredBlock(
        block_id="id1",
        filename="a.py",
        start_line=1,
        end_line=2,
        parent_class=None,
        language="python",
        content_hash="h",
        code="def f():\n    return 1\n",
    )
    store.upsert_blocks([block], [[0.0]])
    hits = store.query([0.0], top_k=1)

    assert len(hits) == 1
    assert hits[0].block_id == "id1"
    assert hits[0].filename == "a.py"
    assert "def f" in hits[0].code


def test_indexer_calls_store_with_expected_blocks(tmp_path: Path) -> None:  # pylint: disable=unused-variable
    (tmp_path / "x.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    captured: list[StoredBlock] = []

    @dataclass(frozen=True, slots=True)
    class _FakeStore:
        def upsert_blocks(self, blocks: list[StoredBlock], _embeddings: list[list[float]]) -> None:
            captured.extend(list(blocks))

    gitignore = pathspec.PathSpec.from_lines("gitwildmatch", [])
    stats = index_root(
        tmp_path,
        store=cast(VectorStore, _FakeStore()),
        embedder=cast(Embedder, _StubEmbedder()),
        gitignore=gitignore,
    )

    assert stats.files_indexed == 1
    assert stats.blocks_extracted >= 1
    assert stats.blocks_indexed == stats.blocks_extracted
    assert any(b.filename == "x.py" for b in captured)


def test_content_hash_and_block_id_are_stable() -> None:  # pylint: disable=unused-variable
    code = "def f():\n    return 1\n"
    h1 = compute_content_hash(code)
    h2 = compute_content_hash(code)
    assert h1 == h2

    id1 = compute_block_id(filename="a.py", start_line=1, end_line=2, content_hash=h1)
    id2 = compute_block_id(filename="a.py", start_line=1, end_line=2, content_hash=h1)
    assert id1 == id2
