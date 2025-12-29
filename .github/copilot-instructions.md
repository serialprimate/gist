# Copilot Instructions for AI Agents

## Project Overview
**gist** is a CLI tool for polyglot semantic code search using Tree-sitter and vector embeddings. It runs entirely offline for privacy.

**Current Status:** Phase 1 ("No-Churn" Skeleton) - implements codebase traversal and structural code extraction. Phase 2 (vector embeddings/semantic search) is planned but not yet implemented.

**Tech Stack:** Python 3.12+, click (CLI), tree-sitter-languages (parsing), pathspec (gitignore), future: sentence-transformers, chromadb

**Key Files:**
- `src/gist/main.py` - CLI definition using click (entry point via console script)
- `src/gist/__main__.py` - Alternative entry via `python -m gist`
- `src/gist/extractor.py` - Tree-sitter parsing logic for `.py`, `.ts`, `.js`, `.cpp`
- `src/gist/walker.py` - Directory traversal with gitignore/exclusion logic
- `docs/PRD.md` - Product requirements and vision
- `docs/implementation_plan_phase_1.md` - Detailed Phase 1 spec

## Architecture & Data Flow

### Three-Layer Pipeline (Phase 1)
1. **Walker** (`walker.py`): Traverses directories, respects `.gitignore` and hardcoded exclusions (`.git`, `node_modules`, `__pycache__`, etc.), yields supported file paths
2. **Extractor** (`extractor.py`): Parses files with Tree-sitter, identifies function/class nodes, returns `ExtractedCodeBlock` dataclasses with metadata (filename, line range, code, parent_class)
3. **CLI** (`main.py`): `gist index` command walks root, extracts blocks, prints to console for validation

**Critical Design Decisions:**
- Non-overlapping extraction: class blocks include their methods (see tests)
- Parent class resolution: methods track their enclosing class in metadata
- Error tolerance: parsing errors are caught, logged to stderr, and processing continues

### Phase 2 (Planned, Not Implemented)
Will add: vector embeddings (all-MiniLM-L6-v2), ChromaDB persistence in `.gist/` directory, `gist search` command

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

**Critical:** `pythonsetup.sh` uses `pip-compile` (from pip-tools) to pin dependencies. The workflow is:
1. Edit `requirements.in` or `requirements-dev.in` (high-level deps)
2. Run `pip-compile --resolver=backtracking --strip-extras --upgrade <file>.in`
3. Use `pip-sync requirements.txt requirements-dev.txt` to sync environment

**Never** manually edit `.txt` files or run `pip install <package>` directly - breaks deterministic builds.

### Running & Testing
```bash
gist index [ROOT_DIR]       # Run CLI (defaults to current dir)
python -m gist index .      # Alternative invocation
pytest                      # Run tests (uses pytest fixtures, parametrize)
./scripts/pythonclean.sh    # Clean artifacts, remove .venv
```

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
- [PRD](docs/PRD.md) - Vision, phases, future extensions
- [Phase 1 Plan](docs/implementation_plan_phase_1.md) - Implementation details
- [Python Instructions](.github/instructions/python.instructions.md) - Code style guide
