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
    assert run("cat dog to a cat be bird\n") == ["1: a", "2: be to", "3: cat dog", "4: bird"], (
        "'cat' appears twice but is listed once. Lengths go shortest first; words are sorted.")


def test_empty():
    assert run("\n") == []


def test_lengths_sorted_not_first_seen():
    assert run("elephant ox\n") == ["2: ox", "8: elephant"], "Sort by length, not first-seen order."


def test_case_sensitive():
    assert run("Ab ab AB\n") == ["2: AB Ab ab"], "Words are distinct when their case differs."
