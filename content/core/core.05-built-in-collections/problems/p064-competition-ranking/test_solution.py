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
        "1. asha 90", "1. john 90", "3. meena 85", "3. zoe 85", "5. ravi 70", "Distinct scores: 3"]


def test_all_equal():
    assert run("3\nc 5\nb 5\na 5\n") == ["1. a 5", "1. b 5", "1. c 5", "Distinct scores: 1"]


def test_skips_after_tie():
    out = run("4\na 10\nb 10\nc 10\nd 1\n")
    assert out[3] == "4. d 1", "Three players are above d, so d's rank is 4 (not 2)."


def test_empty():
    assert run("0\n") == ["Distinct scores: 0"]


def test_large_is_fast():
    n = 100000
    lines = [str(n)] + [f"p{i:06d} {i % 1000}" for i in range(n)]
    out = run("\n".join(lines) + "\n")
    assert out[-1] == "Distinct scores: 1000" and out[0] == "1. p000999 999" and out[100] == "101. p000998 998", (
        "100 players share each score. Rank = first position of that score in sorted order. "
        "Counting higher scores per player is O(n^2) and too slow.")
