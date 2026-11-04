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

import random


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a, k):
    total = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s % k == 0:
                total += 1
    return total


def by_sorting(a, k):
    """Independent check: sort the prefix remainders and count equal pairs in each run."""
    rems = [0]
    s = 0
    for x in a:
        s += x
        rems.append(s % k)
    rems.sort()
    total = 0
    run_len = 1
    for i in range(1, len(rems)):
        if rems[i] == rems[i - 1]:
            run_len += 1
        else:
            total += run_len * (run_len - 1) // 2
            run_len = 1
    return total + run_len * (run_len - 1) // 2


@pytest.mark.parametrize("a, k, want, why", [
    ([4, 5, 0, -2, -3, 1], 5, 7, "the example"),
    ([5], 9, 0, "one element that is not a multiple"),
    ([9], 9, 1, "one element that is a multiple: the empty prefix P[0] = 0 must be counted"),
    ([1, 2, 3], 1, 6, "k = 1: every subarray counts, 3 * 4 / 2 = 6"),
    ([0, 0, 0], 7, 6, "zeros: every sum is 0, which is divisible by anything"),
    ([3, 3, 3], 3, 6, "all multiples of k: every subarray counts"),
    ([1, 1, 1], 2, 2, "[1, 1] twice"),
])
def test_examples(a, k, want, why):
    got = ask(a, k)
    assert got == [str(want)], f"a = {a}, k = {k}: expected {want}, got {got} ({why})."


def test_negative_remainders():
    got = ask([-1, 2], 3)
    assert got == ["0"], (
        f"a = [-1, 2], k = 3: the sums are -1, 2 and 1, none divisible by 3, so 0; got {got}. The prefix sums -1 "
        "and 1 have DIFFERENT remainders modulo 3 (2 and 1). Do not use abs(); Python's % already handles negatives.")


def test_negative_matching():
    got = ask([-2, 7], 5)
    assert got == ["1"], (
        f"a = [-2, 7], k = 5: [-2, 7] has sum 5, so 1; got {got}. The prefix sums are 0, -2, 5 with remainders "
        "0, 3, 0 (in Python -2 % 5 is 3): one equal pair. Remember the empty prefix P[0] = 0.")


def test_fmod_is_wrong():
    got = ask([-3, 5, -4, 1], 4)
    assert got == [str(brute([-3, 5, -4, 1], 4))], (
        f"Expected {brute([-3, 5, -4, 1], 4)}, got {got}. Remainders of negative prefixes must be made non-negative "
        "(Python's % does it; math.fmod and C-style % do not).")


def test_random_small_against_brute_force():
    rng = random.Random(54)
    for _ in range(30):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(1, 20))]
        k = rng.randint(1, 9)
        got = ask(a, k)
        assert got == [str(brute(a, k))], f"a = {a}, k = {k}: expected {brute(a, k)}, got {got}."


def test_large_random():
    rng = random.Random(5400)
    a = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    k = 1000
    want = by_sorting(a, k)
    got = ask(a, k, timeout=8)
    assert got == [str(want)], (
        f"n = 200000: expected {want}, got {got}. If it timed out, you check every subarray (O(n^2)); "
        "count equal prefix remainders with a dictionary instead.")


def test_large_all_zero():
    n = 200000
    got = ask([0] * n, 13, timeout=8)
    assert got == [str(n * (n + 1) // 2)], f"200000 zeros: every subarray counts, n(n+1)/2 = {n * (n + 1) // 2}; got {got}."
