# gist

**gist** is a CLI-based polyglot semantic code search engine. It uses Tree-sitter to parse codebases into logical blocks (functions and classes), transforms them into vector embeddings, and allows for natural language queries—all running entirely offline.

> [!NOTE]
> This project is currently in **Phase 1: The "No-Churn" Skeleton**. It supports codebase traversal and structural code extraction. Semantic indexing and search are planned for Phase 2.

## Features

- **Structural Chunking:** Uses Tree-sitter to extract function and class bodies as discrete units.
- **Polyglot Support:** Supports `.py`, `.ts`, `.js`, and `.cpp` files.
- **Context Aware:** Preserves filename, line numbers, and parent class names in metadata.
- **Privacy First:** All processing is performed locally. No code fragments leave your machine.

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

### Indexing (Phase 1)

Currently, you can run the `index` command to verify that `gist` can correctly parse and extract code blocks from your project:

```bash
gist index [ROOT_DIR]
```

If no directory is provided, it defaults to the current directory. It respects `.gitignore` patterns and skips common binary/metadata folders (e.g., `.git`, `node_modules`, `__pycache__`).

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

- **Phase 1 (Current):** Tree-sitter extraction and CLI skeleton.
- **Phase 2:** Vector integration with `sentence-transformers` and `chromadb`.
- **Phase 3:** Search UI with `rich` and incremental indexing.

## License

MIT
