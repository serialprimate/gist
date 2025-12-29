# Implementation Plan: Phase 1 – The "No-Churn" Skeleton

## Technical Overview

This phase establishes the foundational pipeline for the `gist` CLI tool, enabling codebase traversal and extraction of
function/class blocks using Tree-sitter. The goal is to verify that the parser can correctly identify and extract code
units from supported languages, printing them to the console for validation. No persistent storage or semantic indexing
is introduced in this phase.

Refer to the PRD section 4, Phase 1: The "No-Churn" Skeleton for the original detailed requirements.

## Proposed Changes

### 1. Project Initialisation
- Confirm `pyproject.toml` defines the `gist` CLI entry point (already present).
- Ensure the main logic is routed through `src/gist/main.py` and invoked by `src/gist/__main__.py`.

### 2. Tree-sitter Extractor Logic
- Add a new module: `src/gist/extractor.py`.
- Implement a class or function to:
  - Detect file types (`.py`, `.ts`, `.js`, `.cpp`).
  - Use `tree-sitter-languages` to parse files and extract function/class nodes.
  - Return extracted code blocks with metadata (filename, start/end line, parent class if applicable).

### 3. CLI `index` Command
- Integrate `click` in `main.py` to provide a CLI interface.
- Add an `index` command that:
  - Recursively walks the project directory (excluding `.git`, `node_modules`, binaries).
  - For each supported file, invokes the extractor and prints each code block with metadata.

### 4. Directory Exclusion Logic
- Exclude `.git/` and parse `.gitignore` to determine additional files/directories to skip.
- Also skip common binary folders (e.g., `node_modules`, `dist`, etc.).

### 5. Code Structure
- All new modules and logic reside in `src/gist/`.
- Use type hints and docstrings for all public functions/classes.

## Data Schema / API Contracts

```python
# Example: ExtractedCodeBlock (Python)
from typing import Optional

class ExtractedCodeBlock:
    filename: str
    start_line: int
    end_line: int
    code: str
    parent_class: Optional[str]  # Always attempt to resolve if it exists
```

## Observability & Testing

- **Unit Tests:**
  - Test extractor logic on sample files for each supported language.
  - Test directory walking, `.gitignore` parsing, and exclusion logic.
  - Test CLI integration (e.g., `gist index` end-to-end output).
**Manual Verification:**
  - Run `gist index` on a sample project and verify printed output matches expected code blocks.
**Logging:**
  - Print all errors and warnings to the console during indexing (including parse errors, file read errors, and unsupported file types).

## Next Steps
- Proceed to implement the above modules and logic.
- Prepare for Phase 2: Vector integration and persistence.
