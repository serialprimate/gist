# Implementation Plan: Phase 2 - Vector Integration

PRD implementation phase in scope: "Phase 2: Vector Integration (4-6 Hours)".

This document describes how to extend the current Phase 1 extraction skeleton into a functional semantic index and search
CLI. It is written to fit the existing architecture:

- Walker: iterates supported files while respecting `.gitignore` and default excludes
- Extractor: returns `ExtractedCodeBlock` instances from Tree-sitter
- CLI: currently implements `gist index` for printing extracted blocks

Lines in this document are wrapped at 120 characters. Code snippets are wrapped at 80 characters.

---

## 1. Technical Overview

Phase 2 introduces an on-disk vector index stored under `.gist/` in the project root and a new `gist search` command.

Key architectural additions:

- **Embedding layer**: a small abstraction around `sentence-transformers`.
  - Default embedder: `all-MiniLM-L6-v2` (384-dim vectors).
  - Must download on first use and cache locally (handled by underlying libraries).
- **Vector store layer**: a thin wrapper around `chromadb` in persistent mode.
  - Collection name: `code`.
  - Stores embeddings, code text, and metadata required for display and filtering.
- **Indexing flow** (`gist index`):
  - Walk root -> extract blocks -> embed -> upsert into Chroma.
  - For PoC, full re-index is acceptable; design should keep a place for hashes.
- **Search flow** (`gist search "<query>"`):
  - Load embedder + persistent DB -> embed query -> vector search -> show top 3.

Non-goals for Phase 2 (explicitly defer to Phase 3):

- Rich progress bars / syntax highlighting (though we should keep output structured enough to add later)
- Incremental re-indexing by file hash (we will store hashes to enable it later)

---

## 2. Proposed Changes (File-by-File)

### 2.1 Dependencies

- Update `requirements.in` to include:
  - `sentence-transformers`
  - `chromadb`

Notes:

- Do not edit `requirements.txt` or `requirements-dev.txt` by hand.
- Use the existing `scripts/pythonsetup.sh` flow to `pip-compile` and `pip-sync`.

### 2.2 New Module: `src/gist/embeddings.py`

Purpose: provide an embedding API that is testable without downloading models.

Responsibilities:

- Define a small protocol for embedders.
- Provide a `SentenceTransformerEmbedder` implementation.
- Provide a factory `get_default_embedder()`.

Recommended interface:

```python
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class Embedder(Protocol):
    dimension: int

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_query(self, query: str) -> list[float]:
        ...


@dataclass(frozen=True, slots=True)
class SentenceTransformerEmbedder:
    model_name: str = "all-MiniLM-L6-v2"

    @property
    def dimension(self) -> int:
        return 384

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_query(self, query: str) -> list[float]:
        ...
```

Test strategy detail:

- Unit tests should stub `Embedder` to avoid network downloads.
- `SentenceTransformerEmbedder` should be covered by a small smoke test that can be opted-in (see clarifications).

### 2.3 New Module: `src/gist/store.py`

Purpose: encapsulate Chroma persistence, collection creation, and common operations.

Responsibilities:

- Resolve `.gist/` paths.
- Create/open a `chromadb.PersistentClient`.
- Create/open a `code` collection.
- Upsert blocks (IDs, embeddings, documents, metadata).
- Query top-k results.

Key decisions:

- Persist under `${root}/.gist/chroma/`.
- Keep schema in metadata only (Chroma is schemaless; metadata keys become the contract).

Suggested types:

```python
from __future__ import annotations

from dataclasses import dataclass


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
```

Metadata contract (stored in Chroma):

- `filename`: string (absolute path or root-relative; see clarifications)
- `start_line`: int
- `end_line`: int
- `parent_class`: string | null
- `language`: string (`python`, `javascript`, `typescript`, `cpp`)
- `content_hash`: string (sha256 of `code`, or of file slice)

### 2.4 New Module: `src/gist/indexer.py`

Purpose: the pure logic of building/updating an index.

Responsibilities:

- Walk files with `iter_supported_files()`.
- Extract blocks with `extract_code_blocks()`.
- Compute stable IDs for blocks.
- Batch embed and upsert into store.

Stable IDs recommendation:

- Deterministic ID based on `(relative_filename, start_line, end_line, hash(code))`.
- This makes re-indexing idempotent and enables future incremental strategies.

Suggested helper functions:

- `compute_content_hash(code: str) -> str`
- `compute_block_id(...) -> str`
- `index_root(root: Path, *, store: VectorStore, embedder: Embedder) -> IndexStats`

### 2.5 Update: `src/gist/main.py`

Add a new command: `gist search`.

#### `gist index` behaviour

Finalised behaviour (per clarifications 2B and 4A):

- Default to quiet indexing output: print a short summary rather than all extracted blocks.
- Rebuild the index on every run (wipe and recreate the Chroma persistence directory).

Implementation detail:

- Load gitignore via `load_gitignore_spec(root)` (existing).
- Remove `${root}/.gist/chroma/` if it exists, then recreate it.
- Initialise `embedder = get_default_embedder()`.
- Initialise `store = open_store(root)`.
- For each file: extract blocks; batch embed; upsert.
- Print a final summary (files scanned, blocks extracted, blocks indexed).
- Errors remain best-effort (continue on file-level failures).

#### `gist search "<query>"` behaviour

- Validate index exists (e.g., `.gist/chroma` present). If missing, error and instruct the user to run `gist index`.
- Embed query via embedder.
- Query Chroma collection, request top 3.
- Print results including:
  - filename
  - line range
  - parent class (if present)
  - a short code preview (full snippet is acceptable for PoC)

Command signature:

```python
@cli.command("search")
@click.argument("query", type=str)
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True,
                    path_type=Path),
    required=False,
    default=Path("."),
)
def search(query: str, root: Path) -> None:
    ...
```

Rationale:

- PRD requires `gist search "<query>"`.
- Accepting an optional `ROOT` matches the existing `index` command pattern.

Offline note (per clarification 5A):

- First-run model download is allowed (handled by `sentence-transformers`); subsequent runs should work offline.

### 2.6 Update: `src/gist/walker.py`

No functional changes required.

Potential small addition:

- Export a helper to normalise file paths relative to the root for metadata.

This is optional; we can keep normalisation in `indexer.py`.

### 2.7 Update: `src/gist/extractor.py`

No changes required for Phase 2.

If we later need more context for better embeddings, we can extend metadata, but avoid scope creep in Phase 2.

---

## 3. Data Schema / API Contracts

### 3.1 Vector Store Layout

On-disk layout:

- `.gist/`
  - `chroma/` (Chroma persistence directory)

Chroma collection:

- Collection name: `code`
- Upsert payload:
  - `ids`: list[str]
  - `documents`: list[str] (the code snippet)
  - `embeddings`: list[list[float]]
  - `metadatas`: list[dict[str, object]]

### 3.2 Metadata Schema

Python type describing stored metadata:

```python
from __future__ import annotations

from typing import TypedDict


class CodeBlockMetadata(TypedDict):
    filename: str
    start_line: int
    end_line: int
    parent_class: str | None
    language: str
    content_hash: str
```

Constraints:

- `start_line` and `end_line` are 1-based, matching current extractor output.
- `language` must align with `detect_language()` return values.
- `filename` is stored root-relative (portable across machines and stable for deterministic IDs).

### 3.3 Hashing Contract (Future-Proofing)

For Phase 2, we still write hashes to enable Phase 3/4 incremental indexing.

Recommended:

- `content_hash = sha256(code.encode("utf-8"))`

This is stable across platforms and avoids needing to re-slice the file later.

---

## 4. Observability & Testing

### 4.1 Logging / Errors

Maintain the existing Phase 1 posture: report and continue.

- File-level failures:
  - Catch broad exceptions around extract/embed/store for each file
  - Print to stderr: `[error] <path>: <exception>`
- Store-level failures:
  - If the store cannot be opened, fail fast (search must not proceed)

### 4.2 Unit Tests

Add tests under `tests/` for the new modules:

1. `test_embeddings_stub_usage`
   - Use a fake embedder returning fixed-size vectors.
   - Ensure `indexer` calls embedder with expected texts.

2. `test_store_roundtrip_with_fake_embeddings`
   - Create a temp root dir.
   - Open store under `.gist/`.
  - Upsert 1-2 blocks with known metadata.
   - Query and assert returned metadata matches.

3. `test_cli_search_errors_without_index`
   - Run `gist search` on a temp dir without `.gist/`.
   - Assert non-zero exit code and a helpful error message.

4. `test_cli_index_then_search_with_stub_embedder`
   - Monkeypatch `get_default_embedder()` to a stub.
   - Run `gist index` then `gist search`.
   - Assert top result points to expected file and includes code.

Network avoidance requirement:

- Tests must not download `all-MiniLM-L6-v2`.
- Stub embedder is mandatory for deterministic CI.

### 4.3 Integration / Smoke Tests (Optional)

If desired, add an opt-in smoke test that uses the real model:

- Mark with `@pytest.mark.slow` and skip unless env var is set.

---

## 5. Finalised Decisions

Incorporating clarifications:

- `filename` in metadata: root-relative paths
- `gist index` output: quiet by default, print summary
- `gist search` on missing index: error, instruct to run `gist index`
- Re-index behaviour: always wipe and rebuild the collection
- Embeddings offline behaviour: allow first-run download, offline thereafter

---

## 6. Rollout Steps

1. Add new dependencies to `requirements.in`.
2. Implement `embeddings.py`, `store.py`, `indexer.py`.
3. Wire into `gist index` without breaking existing output.
4. Add `gist search` command.
5. Add stub-based tests to prevent model downloads.
