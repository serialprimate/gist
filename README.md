# gist

**gist** is a CLI-based polyglot semantic code search engine. It uses Tree-sitter to parse codebases into logical blocks (functions and classes), transforms them into vector embeddings, and allows for natural language queries.

gist is designed to run locally for privacy. The only time you may need network access is on first use of the default embedding model so it can be downloaded into your local cache.

## Motivation

Searching code by keyword breaks down when you remember intent but not exact names.

gist is for queries like:

- "Where do we validate JWTs?"
- "How do we debounce input events?"
- "Where is the retry/backoff logic implemented?"

Instead of grepping for the right identifier, gist extracts structural code blocks and indexes them into a local vector store so you can search with natural language.

## Features

- **Structural Chunking:** Uses Tree-sitter to extract function and class bodies as discrete units.
- **Polyglot Support:** Supports `.py`, `.ts`, `.js`, and `.cpp` files.
- **Context Aware:** Preserves filename, line numbers, and parent class names in metadata.
- **Local Index:** Stores the vector index under `.gist/` in the target repository.
- **Privacy First:** Indexing and searching run locally.

## Current Limitations

This is still a PoC with some intentional trade-offs:

- **Full re-indexing:** `gist index` currently wipes and rebuilds the index on each run (no incremental updates yet).
- **No progress UI:** Indexing output is minimal; large repositories can take a while with no progress bar.
- **Limited language set:** Only `.py`, `.js`, `.ts`, and `.cpp` are indexed.
- **Model download on first run:** The default embedder (`all-MiniLM-L6-v2`) downloads once and then uses a local cache.
- **Search UX is minimal:** Results are currently top-3 only and printed as plain text.
- **Bloat:** This PoC pulls in several libraries with lots of transitive dependencies.

## Installation

### For Users

You can install `gist` directly from the source:

```bash
pip install .
```

This will install the `gist` command globally (or in your active virtual environment).

### For Developers

1. Clone the repository:
   ```bash
   git clone https://github.com/serialprimate/gist.git
   cd gist
   ```

2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./scripts/pythonsetup.sh
   ```

3. Activate the environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install in editable mode:
   ```bash
   pip install -e .
   ```

## Building the Package

To generate source and wheel distributions:

1. Ensure `build` is installed:
   ```bash
   pip install build
   ```

2. Run the build command:
   ```bash
   python -m build
   ```

The artifacts will be available in the `dist/` directory.

## Usage

### Indexing

Build (or rebuild) a persistent vector index under `.gist/`:

```bash
gist index [ROOT_DIR]
```

If no directory is provided, it defaults to the current directory. It respects `.gitignore` patterns and skips common folders (e.g., `.git`, `node_modules`, `__pycache__`).

### Searching

Query an indexed repository:

```bash
gist search "<query>" [ROOT_DIR]
```

Example:

```bash
gist search "token refresh" .
```

## Project Structure

- `src/gist/`: Main package source.
  - `main.py`: CLI entry point and command definitions.
  - `extractor.py`: Tree-sitter logic for code block extraction.
  - `walker.py`: File system traversal and exclusion logic.
- `tests/`: Unit and integration tests.
- `scripts/`: Automation scripts for setup and cleaning.
- `docs/`: Project documentation (PRD, implementation plans).

## Development

### Running Tests

```bash
pytest
```

### Cleaning the Project

To remove build artifacts, caches, and the virtual environment:

```bash
./scripts/pythonclean.sh
```

## Roadmap

- **Phase 3:** Better UX (progress, formatting), incremental indexing, and richer result display.

## License

MIT
