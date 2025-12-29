"""Code extraction using Tree-sitter.

Phase 1 goal: given a source file, extract function/class blocks and return
structured metadata for printing/validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tree_sitter import Node
from tree_sitter_languages import get_parser  # type: ignore


@dataclass(frozen=True, slots=True)
class ExtractedCodeBlock:
    """A contiguous block of source code extracted from a file."""

    filename: str
    start_line: int
    end_line: int
    code: str
    parent_class: str | None


_SUPPORTED_SUFFIX_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".cpp": "cpp",
}


_LANGUAGE_NODE_TYPES: dict[str, set[str]] = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "class_declaration", "method_definition"},
    "typescript": {"function_declaration", "class_declaration", "method_definition"},
    "cpp": {"function_definition", "class_specifier", "struct_specifier"},
}


_CLASS_NODE_TYPES: dict[str, set[str]] = {
    "python": {"class_definition"},
    "javascript": {"class_declaration"},
    "typescript": {"class_declaration"},
    "cpp": {"class_specifier", "struct_specifier"},
}


def detect_language(path: Path) -> str | None:
    """Detect a supported Tree-sitter language name from a file extension."""

    return _SUPPORTED_SUFFIX_TO_LANGUAGE.get(path.suffix.lower())


def extract_code_blocks(path: Path) -> list[ExtractedCodeBlock]:  # pylint: disable=unused-variable
    """Extract function/class code blocks from a supported source file.

    Args:
        path: Path to the source file.

    Returns:
        A list of extracted blocks (may be empty).

    Raises:
        OSError: If the file cannot be read.
        UnicodeError: If decoding fails.
        ValueError: If the file type is unsupported.
    """

    language = detect_language(path)
    if language is None:
        raise ValueError(f"Unsupported file type: {path}")

    source_bytes = path.read_bytes()
    parser = get_parser(language)
    tree = parser.parse(source_bytes)

    node_types = _LANGUAGE_NODE_TYPES.get(language, set())
    class_node_types = _CLASS_NODE_TYPES.get(language, set())

    blocks: list[ExtractedCodeBlock] = []

    def walk(node: Node) -> None:
        if node.type in node_types:
            parent_class = _resolve_parent_class_name(
                node=node,
                source_bytes=source_bytes,
                language=language,
                class_node_types=class_node_types,
            )
            code = source_bytes[node.start_byte: node.end_byte].decode(
                "utf-8",
                errors="replace",
            )
            blocks.append(
                ExtractedCodeBlock(
                    filename=str(path),
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    code=code,
                    parent_class=parent_class,
                )
            )

            # Granularity choice: avoid overlapping blocks by not extracting
            # descendant functions/methods when a class block is extracted.
            if node.type in class_node_types:
                return

        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return blocks


def _resolve_parent_class_name(
    *,
    node: Node,
    source_bytes: bytes,
    language: str,
    class_node_types: set[str],
) -> str | None:
    def find_parent_class(current: Node | None) -> str | None:
        if current is None:
            return None
        if current.type in class_node_types:
            name_node = current.child_by_field_name("name")
            if name_node is not None:
                return source_bytes[name_node.start_byte: name_node.end_byte].decode(
                    "utf-8",
                    errors="replace",
                )

            # Best-effort fallback for grammars that don't expose a "name" field.
            # Keep this conservative: return None if we can't confidently derive it.
            if language in {"cpp"}:
                for child in current.children:
                    if child.type in {"type_identifier", "identifier"}:
                        return source_bytes[child.start_byte: child.end_byte].decode(
                            "utf-8",
                            errors="replace",
                        )

            return None
        return find_parent_class(current.parent)

    return find_parent_class(node.parent)
