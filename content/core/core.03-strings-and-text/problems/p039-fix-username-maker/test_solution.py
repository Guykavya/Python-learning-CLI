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
    assert run("  asha   rani KUMAR\n 2005\n") == ["Hello, Asha Rani Kumar!", "Username: ashak05", "Age in 2026: 21"], (
        "Check every line against the specification. The tests below point at each bug separately.")


def test_age_line_does_not_crash():
    out = run("ravi verma\n2000\n")
    assert out[2] == "Age in 2026: 26", "You cannot + a string and an int. Use an f-string or str()."


def test_last_two_digits():
    assert run("ravi verma\n2000\n")[1] == "Username: raviv00", (
        "The year part is the LAST two digits: year[-2:]. year[:-2] gives the first two.")


def test_lowercase_username():
    assert run("RAVI VERMA\n1999\n")[1] == "Username: raviv99", (
        "first.lower() on its own line throws the result away. Store it, and lowercase the initial too.")


def test_last_word_not_second():
    assert run("Meena Devi Iyer\n2004\n")[1] == "Username: meenai04", (
        "The initial comes from the LAST word: words[-1], not words[1].")


def test_double_spaces():
    assert run("john    smith\n1990\n") == ["Hello, John Smith!", "Username: johns90", "Age in 2026: 36"], (
        "split(' ') makes empty words when there are double spaces. Use split() with no argument, "
        "and rebuild the greeting from the words with single spaces.")


def test_year_with_spaces():
    assert run("li wei\n 1985 \n") == ["Hello, Li Wei!", "Username: liw85", "Age in 2026: 41"], (
        "Strip the year before slicing; '1985 '[-2:] is '5 '.")


def test_unicode_name():
    assert run("josé ÁLVAREZ\n2001\n")[1] == "Username: joséá01"
