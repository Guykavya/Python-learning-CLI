import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import sum_subarray_mins

HERE = Path(__file__).parent
MOD = 10 ** 9 + 7


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(arr):
    total = 0
    for i in range(len(arr)):
        low = arr[i]
        for j in range(i, len(arr)):
            low = min(low, arr[j])
            total += low
    return total % MOD


@pytest.mark.parametrize("arr, want, why", [
    ([3, 1, 2, 4], 17, "the example"),
    ([11, 81, 94, 43, 3], 444, "the second example"),
    ([2, 2], 6, "equal values: the subarray [2, 2] counts ONCE (strict on one side, not strict on the other)"),
    ([5], 5, "one element"),
    ([1, 1, 1], 6, "six subarrays, each with minimum 1"),
    ([1, 2, 3], 10, "increasing: 1 + 2 + 3 + 1 + 2 + 1"),
    ([3, 2, 1], 10, "decreasing"),
])
def test_cases(arr, want, why):
    got = sum_subarray_mins(list(arr))
    assert got == want, f"sum_subarray_mins({arr}) should be {want}, got {got}: {why}."


def test_random_with_many_ties():
    rng = random.Random(36)
    for _ in range(1000):
        arr = [rng.randint(1, 4) for _ in range(rng.randint(1, 10))]
        assert sum_subarray_mins(list(arr)) == slow(arr), (
            f"sum_subarray_mins({arr}) should be {slow(arr)}. With repeated values, check the tie rule: "
            "previous STRICTLY smaller on the left, next smaller OR EQUAL on the right.")


def test_big_in_time_and_modulo():
    code = (
        "from solution import sum_subarray_mins\n"
        "a = [30000] * 100000\n"
        "b = [(i * 7919) % 30000 + 1 for i in range(100000)]\n"
        "print(sum_subarray_mins(a), sum_subarray_mins(b))\n"
    )
    n = 100000
    want_a = 30000 * n * (n + 1) // 2 % MOD
    b = [(i * 7919) % 30000 + 1 for i in range(n)]
    want = f"{want_a} {fast_ref(b)}"
    out = run_code(code, 20, "sum_subarray_mins on 100,000 numbers (contribution technique, O(n))")
    assert out == want, (f"Expected {want!r}, got {out!r}. All 100,000 equal values: every subarray has minimum 30000; "
                         "did you forget the modulo 10**9 + 7?")


def fast_ref(arr):
    n = len(arr)
    prev, nxt, stack = [-1] * n, [n] * n, []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        prev[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        nxt[i] = stack[-1] if stack else n
        stack.append(i)
    return sum(arr[i] * (i - prev[i]) * (nxt[i] - i) for i in range(n)) % MOD
