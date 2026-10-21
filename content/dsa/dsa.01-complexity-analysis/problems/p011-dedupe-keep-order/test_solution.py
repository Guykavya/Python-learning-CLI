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


def expected_for(values):
    out = list(dict.fromkeys(values))
    return [str(len(out)), " ".join(map(str, out))]


@pytest.mark.parametrize("values, why", [
    ([4, 1, 4, 2, 1, 1, 9, 2], "the example"),
    ([5], "a single value"),
    ([7, 7, 7], "all the same: one value remains"),
    ([3, 2, 1], "no repeats: the order must stay 3 2 1, not sorted"),
    ([-1, 1, -1, 0, 1], "negative numbers and zero are ordinary values"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == expected_for(values), f"Values {values}: expected {expected_for(values)}, got {got} ({why})."


def test_order_is_kept_not_sorted():
    values = [9, 3, 9, 1, 3, 5]
    got = ask(values)
    assert got == ["4", "9 3 1 5"], (
        f"Values {values}: expected ['4', '9 3 1 5'], got {got}. "
        "`set(a)` alone loses the order, and sorting changes it. Keep a list for the order and a set for lookups.")


def test_large_all_different():
    values = [(i * 7919) % 200003 for i in range(200000)]     # 200000 different values, scrambled
    got = ask(values, timeout=5)
    assert got == expected_for(values), (
        "200000 different values: wrong output or too slow. With a list, `x not in result` looks at up to "
        "200000 items for each of 200000 values. Use a set to remember what you have seen.")


def test_large_many_repeats():
    values = [i % 1000 for i in range(200000)]
    got = ask(values, timeout=5)
    assert got == expected_for(values), "200000 values with only 1000 different ones: wrong output or too slow."
