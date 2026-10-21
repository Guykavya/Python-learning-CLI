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
    assert run("1\n2\n2\n") == ["Total: 5.00", "Average: 1.67"]


def test_precedence():
    out = run("3\n3\n3\n")
    assert out[1] == "Average: 3.00", (
        "The average of 3, 3, 3 is 3. If you got 7.00 you wrote a + b + c / 3, "
        "which divides only c. Use brackets: (a + b + c) / 3.")


def test_decimals_and_negatives():
    out = run("-1.5\n1.5\n0\n")
    assert out == ["Total: 0.00", "Average: 0.00"], "Read with float(); negatives and decimals must work."


def test_decimal_result():
    assert run("10\n0\n0\n")[1] == "Average: 3.33", "Show the average with :.2f."
