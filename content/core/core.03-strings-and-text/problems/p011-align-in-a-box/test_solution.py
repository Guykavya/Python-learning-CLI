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
    assert run("cat\n9\n") == ["[cat      ]", "[      cat]", "[   cat   ]", "[***cat***]"]


def test_odd_padding_goes_right():
    out = run("cat\n8\n")
    assert out[2] == "[  cat   ]", "With f-string ^, the extra space goes on the right. str.center() may differ."
    assert out[3] == "[**cat***]"


def test_width_smaller_than_word():
    assert run("elephant\n3\n") == ["[elephant]"] * 4, "Width is a minimum. A longer word is never cut."


def test_unicode():
    assert run("café\n6\n") == ["[café  ]", "[  café]", "[ café ]", "[*café*]"], "é is one character, so café has length 4."


def test_zero_width():
    assert run("hi\n0\n") == ["[hi]"] * 4
