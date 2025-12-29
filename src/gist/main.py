"""CLI entrypoint for gist.

Phase 1 implements `gist index` which walks a project directory, extracts
function/class blocks via Tree-sitter, and prints them for validation.
"""

from __future__ import annotations

from pathlib import Path

import click

from gist.extractor import ExtractedCodeBlock, extract_code_blocks
from gist.walker import iter_supported_files, load_gitignore_spec


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Polyglot semantic code search (Phase 1: extraction skeleton)."""


@cli.command("index")
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=Path("."),
)
def index(root: Path) -> None:
    """Walk ROOT and print extracted code blocks."""

    root = root.resolve()
    gitignore = load_gitignore_spec(root)

    for file_path in iter_supported_files(root, gitignore=gitignore):
        try:
            blocks = extract_code_blocks(file_path)
        except Exception as exc:  # noqa: BLE001 - phase 1: report and continue
            click.echo(f"[error] {file_path}: {exc}", err=True)
            continue

        for block in blocks:
            _print_block(block)


def _print_block(block: ExtractedCodeBlock) -> None:
    header = f"=== {block.filename}:{block.start_line}-{block.end_line}"
    if block.parent_class:
        header += f" parent={block.parent_class}"
    header += " ==="

    click.echo(header)
    click.echo(block.code.rstrip("\n"))
    click.echo("")


def main() -> None:
    """Console-script entrypoint."""

    cli(standalone_mode=True)


if __name__ == "__main__":
    main()
