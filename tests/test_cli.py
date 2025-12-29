from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from gist.main import cli


def test_cli_index_outputs_blocks(tmp_path: Path) -> None:
    sample = tmp_path / "a.py"
    sample.write_text("def f():\n    return 1\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["index", str(tmp_path)])

    assert result.exit_code == 0
    assert "=== " in result.output
    assert "def f" in result.output
