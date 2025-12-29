"""Directory walking and exclusion logic.

Phase 1 goal: iterate supported source files under a root directory while
respecting hard-coded excludes and .gitignore patterns.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pathspec

from gist.extractor import detect_language


_DEFAULT_EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".gist",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".tox",
        ".ruff_cache",
        ".idea",
        ".vscode",
    }
)


def load_gitignore_spec(root: Path) -> pathspec.PathSpec:
    """Load a PathSpec from a .gitignore file under root (if present)."""

    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return pathspec.PathSpec.from_lines("gitwildmatch", [])

    lines = gitignore_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def iter_supported_files(  # pylint: disable=unused-variable
    root: Path,
    *,
    gitignore: pathspec.PathSpec | None = None,
    excluded_dir_names: frozenset[str] = _DEFAULT_EXCLUDED_DIR_NAMES,
) -> Iterator[Path]:
    """Yield supported source files under root.

    Args:
        root: Root directory to walk.
        gitignore: Optional compiled gitignore matcher.
        excluded_dir_names: Directory base names to always skip.

    Yields:
        Paths to files with supported extensions.
    """

    root = root.resolve()
    if gitignore is None:
        gitignore = load_gitignore_spec(root)

    def is_ignored(path: Path) -> bool:
        rel_str = path.relative_to(root).as_posix()
        if path.is_dir() and not rel_str.endswith("/"):
            rel_str += "/"

        return gitignore.match_file(rel_str)

    for current_dir, dirnames, filenames in root.walk():
        # Prune directories in-place so os.walk won't traverse them.
        kept: list[str] = []
        for dirname in dirnames:
            if dirname in excluded_dir_names:
                continue

            candidate = current_dir / dirname
            if is_ignored(candidate):
                continue

            kept.append(dirname)

        dirnames[:] = kept

        for filename in filenames:
            file_path = current_dir / filename

            if detect_language(file_path) is None:
                continue

            if is_ignored(file_path):
                continue

            yield file_path
