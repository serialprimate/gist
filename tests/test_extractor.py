from __future__ import annotations

from pathlib import Path

import pytest

from gist.extractor import detect_language, extract_code_blocks


def test_detect_language() -> None:
    assert detect_language(Path("x.py")) == "python"
    assert detect_language(Path("x.ts")) == "typescript"
    assert detect_language(Path("x.js")) == "javascript"
    assert detect_language(Path("x.cpp")) == "cpp"
    assert detect_language(Path("x.txt")) is None


def test_extract_python_blocks(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text(
        """
class A:
    def m(self):
        return 1

def f(x: int) -> int:
    return x + 1
""".lstrip(),
        encoding="utf-8",
    )

    blocks = extract_code_blocks(path)
    types = {b.code.lstrip().split(None, 1)[0] for b in blocks if b.code.strip()}
    assert {"class", "def"}.issubset(types)

    # Non-overlapping extraction: the class block includes its methods.
    assert any(("class A" in b.code and "def m" in b.code) for b in blocks)


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        (
            "sample.js",
            """
class C { m() { return 1; } }
function f(x) { return x + 1; }
""".lstrip(),
        ),
        (
            "sample.ts",
            """
class C { m(): number { return 1; } }
function f(x: number): number { return x + 1; }
""".lstrip(),
        ),
        (
            "sample.cpp",
            """
struct S { int m() { return 1; } };
int f(int x) { return x + 1; }
""".lstrip(),
        ),
    ],
)
def test_extract_other_languages_smoke(tmp_path: Path, filename: str, source: str) -> None:
    path = tmp_path / filename
    path.write_text(source, encoding="utf-8")

    blocks = extract_code_blocks(path)
    # Smoke test: should parse and typically find at least one block.
    assert isinstance(blocks, list)
    assert len(blocks) >= 1
