"""CLI entrypoint for gist.

Commands:
- `gist index`: (re)build a persistent vector index under `.gist/`.
- `gist search`: semantic search over indexed code blocks.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import click

from gist.embeddings import get_default_embedder
from gist.indexer import index_root
from gist.store import open_store
from gist.walker import load_gitignore_spec


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Polyglot semantic code search."""


@cli.command("index")
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=Path("."),
)
def index(root: Path) -> None:  # pylint: disable=unused-variable
    """Index ROOT into a persistent vector store under `.gist/`."""

    root = root.resolve()

    # PoC behaviour: always wipe and rebuild.
    chroma_dir = root / ".gist" / "chroma"
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)

    gitignore = load_gitignore_spec(root)
    embedder = get_default_embedder()
    store = open_store(root)

    def _on_file_error(file_path: Path, exc: Exception) -> None:
        click.echo(f"[error] {file_path}: {exc}", err=True)

    stats = index_root(
        root,
        store=store,
        embedder=embedder,
        gitignore=gitignore,
        on_file_error=_on_file_error,
    )
    click.echo(
        f"Indexed {stats.files_indexed} file(s), {stats.blocks_indexed} block(s) "
        f"({stats.blocks_extracted} extracted)."
    )


@cli.command("search")
@click.argument("query", type=str)
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=Path("."),
)
def search(query: str, root: Path) -> None:  # pylint: disable=unused-variable
    """Search an indexed ROOT for QUERY and print top results."""

    root = root.resolve()
    chroma_dir = root / ".gist" / "chroma"
    if not chroma_dir.exists():
        raise click.ClickException("No index found. Run `gist index` first.")

    embedder = get_default_embedder()
    store = open_store(root)

    query_embedding = embedder.embed_query(query)
    hits = store.query(query_embedding, top_k=3)

    for hit in hits:
        header = f"=== {hit.filename}:{hit.start_line}-{hit.end_line}"
        if hit.parent_class:
            header += f" parent={hit.parent_class}"
        header += " ==="
        click.echo(header)
        click.echo(hit.code.rstrip("\n"))
        click.echo("")


def main() -> None:
    """Console-script entrypoint."""

    cli(standalone_mode=True)


if __name__ == "__main__":
    main()
