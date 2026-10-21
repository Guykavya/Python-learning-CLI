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
    assert run("one fish two fish\nfish\ncat\n") == ["one cat two cat", "Replacements: 2"]


def test_not_found():
    assert run("hello world\nxyz\nabc\n") == ["hello world", "Replacements: 0"], (
        "When the word is missing, the sentence is unchanged and the count is 0.")


def test_case_sensitive():
    assert run("Fish fish\nfish\ncat\n") == ["Fish cat", "Replacements: 1"], "replace() is case-sensitive: 'Fish' stays."


def test_count_original_not_new():
    assert run("a b a\na\naa\n") == ["aa b aa", "Replacements: 2"], (
        "Count in the original sentence. The new word 'aa' contains 'a', so counting afterwards gives a wrong number.")


def test_inside_words():
    assert run("cat category\ncat\ndog\n") == ["dog dogegory", "Replacements: 2"], (
        "replace() matches inside other words too.")


def test_overlap():
    assert run("aaaa\naa\nb\n") == ["bb", "Replacements: 2"], "Matches do not overlap: 'aa' is found twice in 'aaaa'."


def test_unicode():
    assert run("café café\né\ne\n") == ["cafe cafe", "Replacements: 2"]
