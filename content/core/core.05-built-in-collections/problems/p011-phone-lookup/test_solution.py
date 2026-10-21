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
    assert run("3\nAsha 98200\nRavi 98111\nAsha 90000\n3\nAsha\nMeena\nRavi\n") == [
        "90000", "Not found: Meena", "98111"], (
        "Asha appears twice; the later number replaces the earlier one.")


def test_case_sensitive():
    assert run("1\nasha 1\n1\nAsha\n") == ["Not found: Asha"], "Names are case-sensitive."


def test_leading_zero_kept():
    assert run("1\nKiran 0712\n1\nKiran\n") == ["0712"], (
        "Keep numbers as strings so a leading zero is not lost.")


def test_no_queries():
    assert run("1\nA 1\n0\n") == [], "With m = 0, print nothing."


def test_many_lookups_fast():
    n = 50000
    lines = [str(n)] + [f"p{i} {i}" for i in range(n)] + [str(n)] + [f"p{i}" for i in range(n)]
    out = run("\n".join(lines) + "\n")
    assert len(out) == n and out[-1] == str(n - 1), (
        "Use a dict. Searching a list of pairs for every query is far too slow for 50,000 queries.")
