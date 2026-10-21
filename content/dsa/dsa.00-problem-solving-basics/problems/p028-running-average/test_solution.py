import ast
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


def called_names() -> set[str]:
    """Names of every plain function call in your solution, e.g. {'print', 'int', 'input'}."""
    tree = ast.parse(SOLUTION.read_text())
    return {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def feed(*nums: int) -> list[str]:
    return run("".join(f"{x}\n" for x in nums) + "0\n")


def expected_for(nums) -> list[str]:
    out, total = [], 0
    for i, x in enumerate(nums, start=1):
        total += x
        out.append(f"{total / i:.2f}")
    return out + [f"count {len(nums)}"]


def test_example():
    got = feed(4, 1, 7)
    assert got == ["4.00", "2.50", "4.00", "count 3"], (
        f"For 4 1 7 then 0 expected 4.00, 2.50, 4.00, count 3. Got {got}. "
        "Use / (not //) and the format :.2f.")


def test_first_is_zero():
    got = run("0\n")
    assert got == ["count 0"], (
        f"When the first line is 0 there is no data: print only 'count 0'. Got {got}. "
        "Do not divide by the count outside the loop.")


def test_one_value():
    got = feed(5)
    assert got == ["5.00", "count 1"], f"For 5 then 0 expected 5.00 and count 1. Got {got}."


def test_zero_not_counted():
    got = feed(2, 4)
    assert got == ["2.00", "3.00", "count 2"], (
        f"For 2 4 then 0 expected 2.00, 3.00, count 2. Got {got}. The 0 is a stop signal: "
        "do not add it or count it.")


def test_two_decimals_always():
    got = feed(1, 2, 3)
    assert got == ["1.00", "1.50", "2.00", "count 3"], (
        f"Every average must show exactly two decimals (2.00, not 2.0 or 2). Got {got}.")


def test_negatives():
    got = feed(-3, 2)
    assert got == ["-3.00", "-0.50", "count 2"], f"For -3 2 expected -3.00, -0.50, count 2. Got {got}."


def test_repeating_decimals():
    got = feed(1, 1, 2)
    assert got == ["1.00", "1.00", "1.33", "count 3"], f"4 / 3 should print as 1.33. Got {got}."


@pytest.mark.parametrize("nums", [
    (10, -10, 10, -10),
    (1000000, 1000000, -1000000),
    (7, 3, 9, 11, 2, 8),
])
def test_various(nums):
    expected = expected_for(nums)
    got = feed(*nums)
    assert got == expected, f"For {nums} then 0 expected {expected}, got {got}."


def test_long_input():
    nums = [(i * 37) % 2001 - 1000 or 1 for i in range(100000)]
    expected = expected_for(nums)
    got = feed(*nums)
    assert len(got) == len(expected), f"Expected {len(expected)} lines, got {len(got)}."
    assert got[-1] == expected[-1] and got[-2] == expected[-2], (
        f"Expected the last lines {expected[-2:]}, got {got[-2:]}.")
