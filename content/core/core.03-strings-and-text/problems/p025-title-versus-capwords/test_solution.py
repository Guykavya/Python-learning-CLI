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


def test_example():
    assert run("they're   ROCK'N'ROLL fans\n") == [
        "title: They'Re   Rock'N'Roll Fans",
        "capwords: They're Rock'n'roll Fans",
        "capitalize: They're   rock'n'roll fans",
    ], "Import string and call string.capwords(text). The three tools treat apostrophes and spaces differently."


def test_capwords_collapses_spaces():
    assert run("  a   tale  \n")[1] == "capwords: A Tale", "capwords splits on whitespace and joins with single spaces."


def test_title_keeps_spaces():
    assert run("  a   tale  \n")[0] == "title:   A   Tale", "title() keeps every space (only the end of the line is ignored by the checker)."


def test_capitalize_first_character_only():
    assert run("hello WORLD\n")[2] == "capitalize: Hello world", "capitalize() uppercases the first character and lowercases the rest."


def test_unicode():
    assert run("école ÉTÉ\n") == ["title: École Été", "capwords: École Été", "capitalize: École été"]
