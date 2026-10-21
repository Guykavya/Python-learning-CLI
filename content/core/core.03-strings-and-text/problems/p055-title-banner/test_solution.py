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
    assert run("Strings & Text\n22\n") == ["+--------------------+", "|   Strings & Text   |", "+--------------------+"]


def test_every_line_is_w_wide():
    out = run("Hello\n15\n")
    assert [len(line) for line in out] == [15, 15, 15], "All three lines must be exactly W characters wide."


def test_extra_space_on_right():
    assert run("ab\n11\n")[1] == "|   ab    |", (
        "With uneven padding the extra space goes on the RIGHT, as f-string ^ does. str.center may differ.")


def test_long_title_shortened():
    out = run("The Complete Guide to Python Strings and Text\n24\n")
    assert out[1] == "|   The Complete...    |", (
        "Titles that do not fit are cut at a word boundary with '...'. Use textwrap.shorten.")


def test_single_huge_word():
    assert run("Supercalifragilisticexpialidocious\n12\n")[1] == "|   ...    |", (
        "If even the first word does not fit, shorten() returns only the placeholder.")


def test_spaces_collapsed():
    assert run("  big    gap  \n14\n")[1] == "|  big gap   |", "shorten() collapses runs of whitespace."


def test_empty_title():
    assert run("\n10\n") == ["+--------+", "|        |", "+--------+"]


def test_unicode_title():
    assert run("Café 🙂\n12\n")[1] == "|  Café 🙂  |"
