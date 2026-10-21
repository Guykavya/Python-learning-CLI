import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


@pytest.mark.parametrize("values, expected, why", [
    ([3, 1, 4, 1, 5], "YES", "1 appears twice"),
    ([10, 20, 30, 40], "NO", "all different"),
    ([7], "NO", "a single number cannot repeat"),
    ([-2, 2, -2], "YES", "-2 appears twice; 2 is a different value"),
    ([5, 5], "YES", "the smallest possible repeat"),
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 1], "YES", "the repeat is at the two ends"),
    ([0, -1, 1], "NO", "0, -1 and 1 are three different values"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [expected], f"Input {values}: expected {expected}, got {got} ({why})."


def test_large_all_different():
    values = list(range(1, 200001, 1))
    values = values[::2] + values[1::2]          # 200000 different values, mixed order
    got = ask(values, timeout=5)
    assert got == ["NO"], (
        f"200000 different numbers: expected ['NO'], got {got}. If this timed out, you still compare every "
        "pair. Remember the values you have already seen in a set, so each check is O(1).")


def test_large_repeat_at_end():
    values = [i * 7 - 10**8 for i in range(200000)]
    values[-1] = values[0]
    got = ask(values, timeout=5)
    assert got == ["YES"], (
        f"200000 numbers whose only repeat is the first and last: expected ['YES'], got {got}. "
        "A pair-by-pair check needs about 2 * 10^10 comparisons here.")
