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
    assert run("5\nravi 70\nasha 90\nmeena 85\njohn 90\nzoe 85\n") == [
        "1. asha 90", "2. john 90", "3. meena 85"], (
        "Ties are broken alphabetically. Sorting (score, name) with reverse=True puts john before asha.")


def test_fewer_than_three():
    assert run("2\nb 1\na 2\n") == ["1. a 2", "2. b 1"], "With two people, print two lines."


def test_none():
    assert run("0\n") == ["No scores."]


def test_numbers_not_text():
    assert run("3\nx 9\ny 10\nz 100\n") == ["1. z 100", "2. y 10", "3. x 9"], (
        "Convert scores to int. As text, '9' sorts after '100'.")


def test_negative_scores():
    assert run("3\na -1\nb -5\nc 0\n") == ["1. c 0", "2. a -1", "3. b -5"]
