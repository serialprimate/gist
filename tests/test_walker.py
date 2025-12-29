from __future__ import annotations

from pathlib import Path

from gist.walker import iter_supported_files, load_gitignore_spec


def test_iter_supported_files_respects_gitignore(tmp_path: Path) -> None:  # pylint: disable=unused-variable
    (tmp_path / ".gitignore").write_text("ignored.py\nsubdir/\n", encoding="utf-8")

    (tmp_path / "kept.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
    (tmp_path / "ignored.py").write_text("def no():\n    return 0\n", encoding="utf-8")

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "x.py").write_text("def nope():\n    return 2\n", encoding="utf-8")

    spec = load_gitignore_spec(tmp_path)
    found = {p.name for p in iter_supported_files(tmp_path, gitignore=spec)}

    assert "kept.py" in found
    assert "ignored.py" not in found
    assert "x.py" not in found
