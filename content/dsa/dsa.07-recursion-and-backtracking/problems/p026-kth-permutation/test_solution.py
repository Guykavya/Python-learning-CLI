import itertools
import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import kth_permutation

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


@pytest.mark.parametrize("n, k, want, why", [
    (3, 1, "123", "the first permutation is the digits in order"),
    (3, 3, "213", "the example"),
    (3, 6, "321", "the last permutation is the digits reversed"),
    (4, 9, "2314", "the 9th of 24"),
    (4, 6, "1432", "the last one of the block starting with 1: use k - 1 (0-based)"),
    (4, 7, "2134", "the first one of the block starting with 2"),
    (1, 1, "1", "one digit"),
])
def test_cases(n, k, want, why):
    got = kth_permutation(n, k)
    assert got == want, f"kth_permutation({n}, {k}) should be {want!r} ({why}), got {got!r}."


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_every_k_small_n(n):
    digits = "".join(str(d) for d in range(1, n + 1))
    for k, p in enumerate(itertools.permutations(digits), 1):
        got = kth_permutation(n, k)
        assert got == "".join(p), f"kth_permutation({n}, {k}) should be {''.join(p)!r}, got {got!r}."


def test_returns_string():
    assert isinstance(kth_permutation(3, 2), str), "Return a string such as '132', not a list."


def test_n9_many_queries_fast():
    rng = random.Random(26)
    ks = [rng.randint(1, 362880) for _ in range(300)] + [1, 200000, 362880]
    want = {}
    sorted_ks = sorted(set(ks))
    j = 0
    for idx, p in enumerate(itertools.permutations("123456789"), 1):
        if idx == sorted_ks[j]:
            want[idx] = "".join(p)
            j += 1
            if j == len(sorted_ks):
                break
    code = ("from solution import kth_permutation\n"
            f"ks = {ks}\n"
            "print(' '.join(kth_permutation(9, k) for k in ks))\n")
    out = run_code(code, 15, "303 queries with n = 9 (count blocks of (n-1)! instead of generating permutations)").split()
    for k, g in zip(ks, out):
        assert g == want[k], f"kth_permutation(9, {k}) should be {want[k]}, got {g}."
    assert len(out) == len(ks), "One answer per query was expected."
