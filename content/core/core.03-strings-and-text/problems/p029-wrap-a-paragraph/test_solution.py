import os
import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines.

    Spaces at the end of each line are ignored, and so are blank lines at the very end.
    """
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin, capture_output=True,
                       text=True, encoding="utf-8", timeout=10,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    lines = [line.rstrip() for line in r.stdout.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


import textwrap


def test_example():
    assert run("20\nStrings are immutable sequences of Unicode code points.\n") == [
        "Strings are", "immutable sequences", "of Unicode code", "points.",
        "--------------------", "Strings are ...",
    ], "Use textwrap.fill for the paragraph and textwrap.shorten with placeholder=' ...' for the preview."


def test_short_text_not_shortened():
    assert run("30\nShort and sweet.\n") == ["Short and sweet.", "-" * 30, "Short and sweet."], (
        "Text that already fits is not changed and gets no placeholder.")


def test_no_line_too_long():
    text = "The quick brown fox jumps over the lazy dog " * 5
    out = run("25\n" + text + "\n")
    body = out[:out.index("-" * 25)]
    assert all(len(line) <= 25 for line in body), "Every wrapped line must be at most `width` characters."
    assert body == textwrap.wrap(text, 25)


def test_preview_fits():
    text = "Unicode text like café and naïve wraps just like ASCII text does"
    out = run("24\n" + text + "\n")
    assert out[-1] == "Unicode text like ...", "The preview must fit in the width, including ' ...'."
    assert len(out[-1]) <= 24
