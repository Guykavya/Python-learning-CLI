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


EXPECTED = [
    "Name         Score",
    "------------------",
    "Asha            87",
    "Ravi            92",
    "Meena            9",
    "------------------",
    "Average       62.7",
]


def test_example():
    assert run("Asha, 87\n  Ravi ,92\nMeena,9\n") == EXPECTED, (
        "Strip each name, convert each score with int(), and use widths 12 and 6.")


def test_header_and_separator():
    out = run("A,1\nB,2\nC,3\n")
    assert out[0] == "Name         Score", "The header uses the same widths: {'Name':<12}{'Score':>6}."
    assert out[1] == "-" * 18 and out[5] == "-" * 18, "The separator lines are 18 dashes."


def test_average_one_decimal():
    assert run("A,10\nB,10\nC,10\n")[6] == "Average       10.0", "The average always shows 1 decimal, even when whole."


def test_names_with_spaces_and_accents():
    out = run("  Zoë Saldana ,100\nJosé,0\nLi, 50\n")
    assert out[2:5] == ["Zoë Saldana    100", "José             0", "Li              50"], (
        "Names can contain spaces and accents. Strip only the ends.")
    assert out[6] == "Average       50.0"
