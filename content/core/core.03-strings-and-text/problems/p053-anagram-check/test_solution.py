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
    assert run("Dormitory\nDirty room!\n") == ["Key 1: dimoorrty", "Key 2: dimoorrty", "Anagrams: True"], (
        "Casefold, delete spaces and punctuation, sort, and join back into a string.")


def test_listen_silent():
    assert run("Listen\nSilent\n")[2] == "Anagrams: True"


def test_counts_matter():
    assert run("aab\nabb\n") == ["Key 1: aab", "Key 2: abb", "Anagrams: False"], (
        "The number of each letter matters. A set would wrongly say True.")


def test_key_is_a_string():
    out = run("cab\nbca\n")
    assert out[0] == "Key 1: abc", "Join the sorted list with ''.join(...) so the key prints as a string."


def test_empty_lines():
    assert run("\n\n") == ["Key 1:", "Key 2:", "Anagrams: True"]


def test_accents():
    assert run("Été\ntéé\n")[2] == "Anagrams: True", "Casefold turns É into é before sorting."
