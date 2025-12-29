from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from gist.main import cli


class _StubEmbedder:
    @property
    def dimension(self) -> int:
        return 1

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        # Deterministic: texts containing "needle" are close to the query.
        return [[0.0] if "needle" in t else [10.0] for t in texts]

    def embed_query(self, query: str) -> list[float]:
        return [0.0 if "needle" in query else 10.0]


def test_cli_index_outputs_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:  # pylint: disable=unused-variable
    def _factory() -> _StubEmbedder:
        return _StubEmbedder()

    monkeypatch.setattr("gist.main.get_default_embedder", _factory)

    sample = tmp_path / "a.py"
    sample.write_text("def needle():\n    return 1\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["index", str(tmp_path)])

    assert result.exit_code == 0
    assert "Indexed" in result.output


def test_cli_search_errors_without_index(tmp_path: Path) -> None:  # pylint: disable=unused-variable
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "needle", str(tmp_path)])
    assert result.exit_code != 0
    assert "No index found" in result.output


def test_cli_index_then_search_with_stub_embedder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:  # pylint: disable=unused-variable
    def _factory() -> _StubEmbedder:
        return _StubEmbedder()

    monkeypatch.setattr("gist.main.get_default_embedder", _factory)

    (tmp_path / "a.py").write_text("def needle():\n    return 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("def other():\n    return 2\n", encoding="utf-8")

    runner = CliRunner()
    index_result = runner.invoke(cli, ["index", str(tmp_path)])
    assert index_result.exit_code == 0

    search_result = runner.invoke(cli, ["search", "needle", str(tmp_path)])
    assert search_result.exit_code == 0
    assert "a.py" in search_result.output
    assert "def needle" in search_result.output
