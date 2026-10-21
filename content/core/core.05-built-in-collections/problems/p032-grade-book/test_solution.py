import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example():
    assert run("asha 80\nravi 70\nasha 90\nmeena 85\nravi 100\nend\n") == [
        "asha: 85.0 (2 marks)", "meena: 85.0 (1 marks)", "ravi: 85.0 (2 marks)"], (
        "All averages are 85.0, so the names decide: alphabetical order.")


def test_empty():
    assert run("end\n") == ["No marks."]


def test_highest_first():
    assert run("a 50\nb 95\nc 9\nend\n") == ["b: 95.0 (1 marks)", "a: 50.0 (1 marks)", "c: 9.0 (1 marks)"], (
        "Sort by the numeric average, highest first.")


def test_average_decimal():
    assert run("x 1\nx 2\nend\n") == ["x: 1.5 (2 marks)"], "Keep every mark for a student and average them."
