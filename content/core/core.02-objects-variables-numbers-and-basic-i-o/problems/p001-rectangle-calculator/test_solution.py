import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example():
    assert run("3\n4.5\n") == ["Area: 13.50", "Perimeter: 15.00"]


def test_whole_numbers_still_show_two_decimals():
    out = run("2\n2\n")
    assert out == ["Area: 4.00", "Perimeter: 8.00"], (
        "Whole numbers must still print with 2 decimals. Look up the :.2f format spec.")


def test_reads_decimals():
    out = run("0.5\n0.25\n")
    assert out[0] == "Area: 0.12" or out[0] == "Area: 0.13", (
        "input() returns a string. Convert it with float(), not int().")
    assert out[1] == "Perimeter: 1.50"


def test_order_is_width_then_height():
    assert run("10\n1\n")[1] == "Perimeter: 22.00"
