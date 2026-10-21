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
    assert run("1234567.891\n") == ["1,234,567.89", "123456789.1%", "1.235e+06", "+1234567.9"]


def test_percent_does_the_multiplying():
    assert run("0.256\n")[1] == "25.6%", "The % type multiplies by 100 for you. Do not multiply again."


def test_zero():
    assert run("0\n") == ["0.00", "0.0%", "0.000e+00", "+0.0"], "Zero still gets 2 decimals, a percent, and a + sign."


def test_negative():
    assert run("-1500.5\n") == ["-1,500.50", "-150050.0%", "-1.500e+03", "-1500.5"], (
        "Negative numbers keep their minus sign; + only adds a sign to positives.")


def test_whole_number_needs_decimals():
    assert run("7\n")[0] == "7.00", "Use .2f so whole numbers still show two decimals."
