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
    assert run("Was it a car or a cat I saw?\n") == ["Cleaned: wasitacaroracatisaw", "Palindrome: True"], (
        "Delete punctuation and whitespace, casefold, then compare with the reverse.")


def test_not_palindrome():
    assert run("Hello, world\n") == ["Cleaned: helloworld", "Palindrome: False"]


def test_punctuation_everywhere():
    assert run("A man, a plan, a canal: Panama!\n") == ["Cleaned: amanaplanacanalpanama", "Palindrome: True"]


def test_tabs_removed():
    assert run("Never\todd or\teven\n") == ["Cleaned: neveroddoreven", "Palindrome: True"], (
        "Tabs are whitespace too. Use string.whitespace, not just ' '.")


def test_empty_and_only_punctuation():
    assert run("\n") == ["Cleaned:", "Palindrome: True"]
    assert run("?!. ,\n") == ["Cleaned:", "Palindrome: True"], "Only punctuation cleans to an empty string, a palindrome."


def test_accents():
    assert run("Ésé\n") == ["Cleaned: ésé", "Palindrome: True"], "casefold turns É into é."


def test_digits_count():
    assert run("12-21\n") == ["Cleaned: 1221", "Palindrome: True"]
