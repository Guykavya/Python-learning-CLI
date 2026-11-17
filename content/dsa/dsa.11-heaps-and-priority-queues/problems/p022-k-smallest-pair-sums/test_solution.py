import itertools
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from solution import k_smallest_pairs

HERE = Path(__file__).parent


def check(a, b, k):
    """Run the learner's function and check every rule; return the pairs."""
    a0, b0 = list(a), list(b)
    got = k_smallest_pairs(a, b, k)
    assert a == a0 and b == b0, "your function changed `a` or `b`."
    assert isinstance(got, list), f"return a list of pairs, not a {type(got).__name__}."
    all_pairs = Counter(itertools.product(a, b))
    want_sums = sorted(x + y for x, y in itertools.product(a, b))[:max(k, 0)]
    pairs = [tuple(p) for p in got]
    assert len(pairs) == len(want_sums), (
        f"a = {a}, b = {b}, k = {k}: expected {len(want_sums)} pairs, got {len(pairs)}. "
        "If k is bigger than the number of pairs, return all of them.")
    sums = [x + y for x, y in pairs]
    assert sums == want_sums, (
        f"a = {a}, b = {b}, k = {k}: the sums should be {want_sums} (smallest first), got {sums}.")
    used = Counter(pairs)
    for pair, times in used.items():
        assert times <= all_pairs[pair], (
            f"a = {a}, b = {b}, k = {k}: the pair {pair} appears {times} times, but only {all_pairs[pair]} such pair(s) exist. "
            "The same cell of the grid was used twice (pushed twice without a seen set?), or the pair does not exist.")
    return pairs


def test_the_examples():
    assert check([1, 7, 11], [2, 4, 6], 3) == [(1, 2), (1, 4), (1, 6)], "first row of the grid."
    check([1, 1, 2], [1, 2, 3], 4)
    assert check([1, 2], [3], 10) == [(1, 3), (2, 3)], "k bigger than the number of pairs: all pairs."


def test_empty_inputs_and_non_positive_k():
    assert k_smallest_pairs([], [1, 2], 3) == [], "a is empty: there are no pairs."
    assert k_smallest_pairs([1, 2], [], 3) == [], "b is empty: there are no pairs."
    assert k_smallest_pairs([1, 2], [3, 4], 0) == [], "k = 0 asks for nothing."
    assert k_smallest_pairs([1, 2], [3, 4], -2) == [], "negative k asks for nothing."


def test_k_of_one():
    assert check([5, 6], [1, 9], 1) == [(5, 1)], "k = 1: the pair of the two smallest numbers."


def test_negative_numbers_and_duplicates():
    check([-5, -5, 0, 3], [-4, -4, 1], 7)
    check([2, 2, 2], [2, 2, 2], 5)


def test_one_list_longer_than_the_other():
    check([1, 2, 3, 4, 5, 6, 7, 8], [1], 5)
    check([1], [1, 2, 3, 4, 5, 6, 7, 8], 5)
    check([0, 100], [0, 1, 2, 3, 4, 5], 8)


def test_all_pairs_when_k_is_big():
    check([1, 3], [2, 4, 6], 6)
    check([1, 3], [2, 4, 6], 100)


@pytest.mark.parametrize("seed", range(80))
def test_random_inputs(seed):
    rng = random.Random(seed)
    spread = rng.choice([2, 6, 40])
    a = sorted(rng.randint(-spread, spread) for _ in range(rng.randint(0, 7)))
    b = sorted(rng.randint(-spread, spread) for _ in range(rng.randint(0, 7)))
    check(a, b, rng.randint(-1, 14))


BIG = """
import resource
try:
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
except Exception:
    pass
from solution import k_smallest_pairs
a = list(range(100000))
b = list(range(100000))
k = 1000
out = k_smallest_pairs(a, b, k)
expected, s = [], 0
while len(expected) < k:
    expected += [s] * (s + 1)
    s += 1
expected = expected[:k]
ok = len(out) == k and [x + y for x, y in out] == expected and len(set(map(tuple, out))) == k
print("OK" if ok else "WRONG")
"""

BIG_DUPLICATES = """
import resource
try:
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
except Exception:
    pass
from solution import k_smallest_pairs
a = [1] * 100000
b = [1] * 100000 + [2]
out = k_smallest_pairs(a, b, 1000)
print("OK" if len(out) == 1000 and all(tuple(p) == (1, 1) for p in out) else "WRONG")
"""


def run_big(code):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "two lists of 100,000 numbers with k = 1000 did not finish in 10 seconds. There are 10 billion pairs: "
            "do not build them. Keep a heap of candidate cells (start with the first column of the first k rows) and "
            "push the right neighbour of every cell you take.")
    if "MemoryError" in r.stderr:
        pytest.fail("you ran out of memory: you built (nearly) all 10 billion pairs. Generate them lazily with a heap.")
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    return r.stdout.strip()


def test_two_lists_of_one_hundred_thousand():
    got = run_big(BIG)
    assert got == "OK", f"big case a = b = range(100000), k = 1000: got {got!r}. The sums must be 0, 1, 1, 2, 2, 2, ... (sum s appears s + 1 times)."


def test_two_lists_of_one_hundred_thousand_equal_numbers():
    got = run_big(BIG_DUPLICATES)
    assert got == "OK", f"100,000 equal numbers in `a`: expected 1000 pairs (1, 1), got {got!r}."
