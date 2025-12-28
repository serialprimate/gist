# PRD: gist (Polyglot Semantic Code Search)

**Project Status:** Weekend Sprint (PoC)
**Primary Stack:** Python 3.12+, `tree-sitter-languages`, `sentence-transformers`, `chromadb`, `click`

---

## 1. Executive Summary

### 1.1 Problem Statement
Developers often waste time searching for code logic using exact keywords. Standard
`grep` fails when the developer remembers the *intent* (e.g., "authentication flow")
but not the specific function names or variable syntax, especially in polyglot
codebases.

### 1.2 Solution
**gist** is a CLI-based semantic search engine. It parses local codebases into
logical blocks using Tree-sitter, transforms them into vector embeddings, and
allows for natural language queries. It runs entirely offline, ensuring privacy.

---

## 2. Technical Architecture & Stack

| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Parsing** | `tree-sitter-languages` | Provides pre-compiled binaries for multi-language support. |
| **Embeddings** | `all-MiniLM-L6-v2` | Fast, CPU-optimised, and fits in <100MB of RAM. |
| **Vector Store** | `chromadb` | Zero-config, persistent SQLite-based local storage. |
| **CLI Framework**| `click` | Industry standard for Python-based terminal applications. |
| **Formatting** | `rich` | For syntax highlighting and progress bars in the terminal. |

---

## 3. Functional Requirements

### 3.1 Ingestion & Parsing
* **Automatic Language Detection:** Identify `.py`, `.ts`, `.js`, and `.cpp` files.
* **Structural Chunking:** Use Tree-sitter to extract function and class bodies
  as discrete units.
* **Context Preservation:** Attach filename, line numbers, and the parent class
  name (if applicable) to each chunk metadata.

### 3.2 Semantic Indexing
* **Vectorisation:** Convert code blocks into 384-dimension vectors.
* **Local Persistence:** Store index data in a `.gist/` directory within the
  project root.
* **Incremental Updates:** For the PoC, a full re-index is acceptable; however,
  the architecture must support hash-based change detection in future versions.

### 3.3 Search Interface
* **Natural Language Query:** Accept raw text via `gist search "<query>"`.
* **Ranked Results:** Return the top 3 snippets based on cosine similarity.
* **Visual Output:** Display the filename, line number, and a syntax-highlighted
  code preview using `rich`.

---

## 4. Implementation Roadmap (The Weekend Sprint)

### Phase 1: The "No-Churn" Skeleton (4-6 Hours)
* **Objective:** Establish the data pipeline from file system to extractor.
* **Task 1:** Initialise project with `pyproject.toml` and console script entry.
* **Task 2:** Implement `tree-sitter` extractor logic using the
  `tree-sitter-languages` library to identify function/class nodes.
* **Task 3:** Create a basic CLI `index` command that walks the directory and
  prints the extracted text to verify the parser.

### Phase 2: Vector Integration (4-6 Hours)
* **Objective:** Enable semantic understanding.
* **Task 1:** Integrate `sentence-transformers`. Ensure the model downloads
  automatically on first run to a local cache.
* **Task 2:** Hook up `chromadb` in persistent mode. Implement logic to add
  chunks and metadata to the "code" collection.
* **Task 3:** Implement the `search` command logic:
  Query -> Embed -> Vector Search -> Results.

### Phase 3: UX & Deployment Prep (4-6 Hours)
* **Objective:** Polish for public sharing.
* **Task 1:** Use `rich` to style search results. Add a progress bar for the
  indexing phase.
* **Task 2:** Document the 1-line installation (via `pip` or `git clone`).
* **Task 3:** Add a `.gitignore` check to ensure `gist` doesn't index
  `node_modules`, `.git`, or binary folders.

---

## 5. Deployment & Distribution Plan

* **Packaging:** Distributed via **PyPI**. The `pyproject.toml` will define a
  `gist` command globally.
* **Portability:** The embedding model is cached in the user's local application
  data directory, making it a "one-click" tool after installation.
* **Privacy:** All processing is performed in-situ. No telemetry or code
  fragments leave the user's machine.

---

## 6. Future Extensions (Post-PoC)

* **Hybrid Search:** Combine semantic results with exact-match string searching
  (leveraging your C++ fast-jsonl experience).
* **Watchdog Mode:** A background daemon that re-indexes modified files on save.
* **IDE Integration:** A VS Code extension that uses the `gist search` CLI as
   a backend for an "AI Jump-to-Definition".
* **Language Support Expansion:** Adding Go, Rust, and Java by registering new
  Tree-sitter grammars.
