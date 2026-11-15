import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import daily_temperatures

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(temps):
    out = []
    for i, t in enumerate(temps):
        out.append(next((j - i for j in range(i + 1, len(temps)) if temps[j] > t), 0))
    return out


@pytest.mark.parametrize("temps, want, why", [
    ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0], "the example"),
    ([30, 40, 50, 60], [1, 1, 1, 0], "rising: always the next day"),
    ([60, 50, 40, 30], [0, 0, 0, 0], "falling: no warmer day ever, so 0 (not -1)"),
    ([], [], "no days"),
    ([50], [0], "one day"),
    ([50, 50, 51], [2, 1, 0], "the same temperature is not warmer: the answer is a DISTANCE"),
    ([70, 30, 30, 30, 80], [4, 3, 2, 1, 0], "everybody waits for the last day"),
])
def test_cases(temps, want, why):
    got = daily_temperatures(list(temps))
    assert got == want, f"daily_temperatures({temps}) should be {want}, got {got}: {why}."


def test_random_against_slow():
    rng = random.Random(28)
    for _ in range(800):
        temps = [rng.randint(30, 36) for _ in range(rng.randint(0, 12))]
        assert daily_temperatures(list(temps)) == slow(temps), f"daily_temperatures({temps}) should be {slow(temps)}."


def test_100000_days_in_time():
    code = (
        "from solution import daily_temperatures\n"
        "temps = [50] * 99999 + [51]\n"
        "w = daily_temperatures(temps)\n"
        "print(sum(w), w[0], w[-1])\n"
    )
    temps = [50] * 99999 + [51]
    want = daily_temperatures_ref(temps)
    out = run_code(code, 20, "daily_temperatures on 100,000 days (use the O(n) stack of indices)")
    assert out == f"{sum(want)} {want[0]} {want[-1]}", f"For the big test expected {sum(want)} {want[0]} {want[-1]}, got {out}."


def daily_temperatures_ref(temps):
    wait = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            wait[j] = i - j
        stack.append(i)
    return wait
