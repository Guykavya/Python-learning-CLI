import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import largest_rectangle

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(heights):
    best = 0
    for i in range(len(heights)):
        low = heights[i]
        for j in range(i, len(heights)):
            low = min(low, heights[j])
            best = max(best, low * (j - i + 1))
    return best


@pytest.mark.parametrize("heights, want, why", [
    ([2, 1, 5, 6, 2, 3], 10, "bars 5 and 6: height 5, width 2"),
    ([2, 4], 4, "bars left on the stack at the end must be measured: use a sentinel 0"),
    ([6, 2, 5, 4, 5, 1, 6], 12, "height 4 across the bars 5, 4, 5"),
    ([], 0, "no bars"),
    ([5], 5, "one bar"),
    ([0, 0], 0, "zero-height bars"),
    ([3, 3, 3], 9, "equal bars: the full width 3"),
    ([1, 2, 3, 4, 5], 9, "increasing: 3 * 3"),
    ([5, 4, 3, 2, 1], 9, "decreasing: 3 * 3; the left edge is index -1 when the stack is empty"),
    ([2, 1, 2], 3, "the low bar in the middle spans everything"),
])
def test_cases(heights, want, why):
    got = largest_rectangle(list(heights))
    assert got == want, f"largest_rectangle({heights}) should be {want}, got {got}: {why}."


def test_does_not_change_input():
    hs = [2, 1, 5]
    largest_rectangle(hs)
    assert hs == [2, 1, 5], "Do not append the sentinel to the caller's list: use heights + [0]."


def test_random_against_slow():
    rng = random.Random(34)
    for _ in range(1000):
        hs = [rng.randint(0, 6) for _ in range(rng.randint(0, 10))]
        assert largest_rectangle(list(hs)) == slow(hs), f"largest_rectangle({hs}) should be {slow(hs)}."


def test_100000_bars_in_time():
    code = (
        "from solution import largest_rectangle\n"
        "hs = [i % 10000 + 1 for i in range(100000)]\n"
        "print(largest_rectangle(hs), largest_rectangle([7] * 100000))\n"
    )
    hs = [i % 10000 + 1 for i in range(100000)]
    want = f"{largest_rectangle_ref(hs)} 700000"
    out = run_code(code, 20, "largest_rectangle on 100,000 bars (use the O(n) stack, not every pair of bars)")
    assert out == want, f"Expected {want!r} for the two big histograms, got {out!r}."


def largest_rectangle_ref(heights):
    stack, best = [], 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best
