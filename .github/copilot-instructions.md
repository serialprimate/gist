# Copilot Instructions for AI Agents

## Project Overview
**gist** is a CLI tool for polyglot semantic code search using Tree-sitter and vector embeddings. It runs entirely offline for privacy.

**Current Status:** Phase 2 Complete - full semantic indexing and search with ChromaDB vector store. Phase 3 (UX enhancements) planned but not implemented.

**Tech Stack:** Python 3.12+, click (CLI), tree-sitter-languages (parsing), pathspec (gitignore), sentence-transformers (embeddings), chromadb (vector store)

**Key Files:**
- `src/gist/main.py` - CLI definition with `index` and `search` commands (entry point: `gist` console script)
- `src/gist/__main__.py` - Alternative entry via `python -m gist`
- `src/gist/extractor.py` - Tree-sitter parsing logic for `.py`, `.ts`, `.js`, `.cpp`
- `src/gist/walker.py` - Directory traversal with gitignore/exclusion logic
- `src/gist/indexer.py` - Indexing pipeline: walk → extract → hash/id → embed → store
- `src/gist/embeddings.py` - Embedding abstraction (Protocol + SentenceTransformer wrapper)
- `src/gist/store.py` - ChromaDB persistence under `.gist/chroma/`
- `docs/PRD.md` - Product requirements and vision
- `docs/implementation_plan_phase_1.md` / `phase_2.md` - Detailed phase specs

## Architecture & Data Flow

### Three-Layer Pipeline (Now Complete)
1. **Walker** (`walker.py`): Traverses directories, respects `.gitignore` and hardcoded exclusions (`.git`, `node_modules`, `__pycache__`, `.gist`, etc.), yields supported file paths
2. **Extractor** (`extractor.py`): Parses files with Tree-sitter, identifies function/class nodes, returns `ExtractedCodeBlock` dataclasses with metadata (filename, line range, code, parent_class)
3. **Indexer** (`indexer.py`): Coordinates walk → extract → hash/embed → store pipeline
4. **Embeddings** (`embeddings.py`): Protocol-based abstraction around `sentence-transformers` (default: all-MiniLM-L6-v2, 384-dim)
5. **Store** (`store.py`): ChromaDB persistence layer storing vectors + metadata in `.gist/chroma/`
6. **CLI** (`main.py`):
   - `gist index [ROOT]` - walks root, extracts blocks, embeds, stores in `.gist/chroma/` (full re-index on each run)
   - `gist search "<query>" [ROOT]` - embeds query, vector search, returns top-3 results with filename:lines

**Critical Design Decisions:**
- Non-overlapping extraction: class blocks include their methods (see tests)
- Parent class resolution: methods track their enclosing class in metadata
- Error tolerance: parsing errors are caught, logged to stderr, and processing continues
- PoC indexing: always wipes `.gist/chroma/` and rebuilds (incremental planned for Phase 3)
- Block identification: stable SHA-256 hash of `filename:start:end:content_hash` for deduplication
- Testability: `Embedder` is a Protocol allowing stub implementations without model downloads

**Data Flow Example:**
```python
# Indexing: file.py → ExtractedCodeBlock → StoredBlock → embedding → ChromaDB
ExtractedCodeBlock(filename="file.py", start_line=5, end_line=10, code="def foo()...", parent_class=None)
  ↓ (compute hash + id)
StoredBlock(block_id="abc123...", ..., content_hash="def456...")
  ↓ (embed_texts via SentenceTransformer)
[0.12, -0.34, ..., 0.56]  # 384-dim vector
  ↓ (upsert to ChromaDB)
Persisted in .gist/chroma/

# Searching: "authentication logic" → embedding → ChromaDB query → SearchHit list
```

## Developer Workflows

### Environment Setup

**Dev Container (Recommended):**
The project includes a complete dev container setup (`.devcontainer/`):
- Based on Ubuntu with Python 3, C++ toolchain (for tree-sitter), and essential tools
- Pre-configured VS Code extensions: python, pylint, isort, mypy, autopep8
- Non-root user (`dev`) with sudo access
- Mounts workspace at `/code/gist` with timezone sync

To use: Open in VS Code and select "Reopen in Container" when prompted.

**Local Setup:**
```bash
./scripts/pythonsetup.sh  # Creates .venv, installs deps with pip-sync
source .venv/bin/activate
pip install -e .           # Editable install for development
```

**Critical:** `pythonsetup.sh` creates a `.venv` and uses `pip-compile` (from pip-tools) to pin dependencies. The workflow is:
1. Edit `requirements.in` or `requirements-dev.in` (high-level deps)
2. Run `pip-compile --resolver=backtracking --strip-extras --upgrade <file>.in`
3. Use `pip-sync requirements.txt requirements-dev.txt` to sync environment

**Never** manually edit `.txt` files or run `pip install <package>` directly - breaks deterministic builds.

### Running & Testing
```bash
gist index [ROOT_DIR]       # Run CLI (defaults to current dir, wipes .gist/chroma/)
gist search "query" [ROOT]  # Search indexed codebase (top-3 results)
python -m gist index .      # Alternative invocation
pytest                      # Run tests (uses pytest fixtures, parametrize)
pytest -v tests/test_phase2.py  # Phase 2 integration tests
./scripts/pythonlint.sh     # Run pylint on all source
./scripts/pythonclean.sh    # Clean artifacts, remove .venv
```

**Testing Patterns:**
- Stub embedders: use Protocol to avoid model downloads in tests (see `test_phase2.py:_StubEmbedder`)
- Fake stores: cast to `VectorStore` to intercept `upsert_blocks` calls
- `tmp_path` fixture for ephemeral file creation
- Parametrize multi-language tests with `@pytest.mark.parametrize`
- Set operations for validation: `assert {"class", "def"}.issubset(types)`

### Building Distribution
```bash
pip install build
python -m build             # Creates dist/*.tar.gz and *.whl
```

## Code Conventions

**Python Standards:**
- Follow `.github/instructions/python.instructions.md` strictly
- Python 3.12+ features: `|` union types, `match`/`case`, `@dataclass` with `slots=True, frozen=True`
- Type hints everywhere: use `str | None` not `Optional[str]`
- Import style: `from __future__ import annotations` at top of every module

**Module Organization:**
- All new features go in `src/gist/` as separate modules
- CLI commands added to `main.py` as `@cli.command()`
- Don't modify entry points (`__main__.py`) unless changing invocation signature

**Error Handling Pattern (see `main.py:index`):**
```python
except Exception as exc:  # noqa: BLE001 - phase 1: report and continue
    click.echo(f"[error] {file_path}: {exc}", err=True)
    continue
```
Phase 1 intentionally catches broad exceptions to avoid stopping indexing on single-file errors.

**Testing Patterns (see `tests/test_extractor.py`):**
- Use `tmp_path` fixture for file creation
- Parametrize multi-language tests with `@pytest.mark.parametrize`
- Validate extraction with set operations: `assert {"class", "def"}.issubset(types)`

## Language Support Details

**Supported Extensions → Tree-sitter Languages:**
- `.py` → python (nodes: `function_definition`, `class_definition`)
- `.js` → javascript (nodes: `function_declaration`, `class_declaration`, `method_definition`)
- `.ts` → typescript (same nodes as JS)
- `.cpp` → cpp (nodes: `function_definition`, `class_specifier`, `struct_specifier`)

**Adding New Languages:**
1. Update `_SUPPORTED_SUFFIX_TO_LANGUAGE` in `extractor.py`
2. Add node types to `_LANGUAGE_NODE_TYPES` and `_CLASS_NODE_TYPES`
3. Verify `tree-sitter-languages` includes the grammar (check PyPI page)
4. Add test case in `test_extractor.py`

## Integration Points

**External Dependencies:**
- `tree-sitter-languages`: Pre-compiled binaries, pinned at 0.20.4 (avoid upgrades without testing)
- `pathspec`: Used for gitignore matching (gitwildmatch format)
- `click`: Context settings include `-h` alias for help

**File System Interaction:**
- `Path.walk()` used for traversal (Python 3.12+, replaces os.walk)
- In-place directory pruning in walker to avoid descending into excluded dirs
- Relative path calculation for gitignore matching: `path.relative_to(root).as_posix()`

## Common Tasks

**Add a CLI command:**
```python
# In main.py
@cli.command("mycommand")
@click.argument("arg", type=click.Path(...))
def mycommand(arg: Path) -> None:
    """Help text."""
    # Implementation
```

**Add language support:**
See "Language Support Details" above

**Modify exclusion logic:**
Edit `_DEFAULT_EXCLUDED_DIR_NAMES` in `walker.py` (frozenset for immutability)

## References
- [PRD](../docs/PRD.md) - Vision, phases, future extensions
- [Phase 1 Plan](../docs/implementation_plan_phase_1.md) - Implementation details
- [Phase 2 Plan](../docs/implementation_plan_phase_2.md) - Semantic search design
- [Python Instructions](instructions/python.instructions.md) - Code style guide
