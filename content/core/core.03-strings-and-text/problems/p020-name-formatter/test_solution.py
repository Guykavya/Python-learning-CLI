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
    assert run("   aDA   byron  LOVELACE\n") == ["Lovelace, Ada", "Initials: A.L."], (
        "Split with no argument, take words[0] and words[-1], and capitalize() each.")


def test_two_words():
    assert run("alan turing\n") == ["Turing, Alan", "Initials: A.T."]


def test_middle_names_ignored():
    assert run("sachin ramesh tendulkar\n") == ["Tendulkar, Sachin", "Initials: S.T."], (
        "The surname is the LAST word (words[-1]), not the second one.")


def test_capitalize_not_title():
    assert run("SEAN o'brien\n") == ["O'brien, Sean", "Initials: S.O."], "Use capitalize(), which lowercases everything after the first letter."


def test_accented_initial():
    assert run("émile zola\n") == ["Zola, Émile", "Initials: É.Z."], "capitalize() works for accented letters."


def test_tabs_and_spaces():
    assert run("\tgrace \t hopper  \n") == ["Hopper, Grace", "Initials: G.H."]
