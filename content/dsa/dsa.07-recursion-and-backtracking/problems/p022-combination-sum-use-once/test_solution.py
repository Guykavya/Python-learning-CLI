import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import combination_sum2

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def norm(result):
    return sorted(sorted(c) for c in result)


def brute(cands, target):
    found = set()
    n = len(cands)
    for mask in range(1 << n):
        pick = [cands[i] for i in range(n) if mask >> i & 1]
        if sum(pick) == target:
            found.add(tuple(sorted(pick)))
    return sorted(list(t) for t in found)


@pytest.mark.parametrize("cands, target, want, why", [
    ([10, 1, 2, 7, 6, 1, 5], 8, [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]], "the example"),
    ([2, 5, 2, 1, 2], 5, [[1, 2, 2], [5]], "three 2s in the input, but [1, 2, 2] only once"),
    ([1, 1, 1, 1], 2, [[1, 1]], "four 1s: [1, 1] once"),
    ([3, 4], 2, [], "no combination"),
    ([2, 2, 2], 6, [[2, 2, 2]], "all three equal values together"),
    ([1, 2], 4, [], "each position at most once: 2 + 2 is not allowed"),
])
def test_cases(cands, target, want, why):
    got = combination_sum2(list(cands), target)
    assert norm(got) == want, f"combination_sum2({cands}, {target}) should be {want} ({why}), got {norm(got)}."


def test_no_duplicates_in_result():
    got = combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)
    keys = [tuple(sorted(c)) for c in got]
    assert len(keys) == len(set(keys)), "A combination appears twice. Sort, then skip a value equal to the previous one at the same level (i > start)."


def test_keeps_first_choice_of_level():
    got = norm(combination_sum2([1, 1, 6], 8))
    assert got == [[1, 1, 6]], "[1, 1, 6] uses two different 1s and must be found. If it is missing you wrote i > 0 instead of i > start."


def test_random_against_brute_force():
    rng = random.Random(22)
    for _ in range(60):
        cands = [rng.randint(1, 8) for _ in range(rng.randint(1, 10))]
        target = rng.randint(1, 20)
        assert norm(combination_sum2(list(cands), target)) == brute(cands, target), \
            f"combination_sum2({cands}, {target}) should give {brute(cands, target)}."


def test_many_equal_values_fast():
    code = "from solution import combination_sum2\nprint(combination_sum2([1] * 30 + [2] * 10, 15) != [])\n"
    out = run_code(code, 20, "combination_sum2([1] * 30 + [2] * 10, 15) (deduplicating with a set at the end explores "
                   "hundreds of millions of branches; skip equal siblings instead)")
    assert out == "True", "combination_sum2([1] * 30 + [2] * 10, 15) has answers, such as fifteen 1s."
    from solution import combination_sum2 as f
    got = norm(f([1] * 30 + [2] * 10, 15))
    want = [[1] * (15 - 2 * k) + [2] * k for k in range(8)]
    assert got == sorted(want), "With 30 ones and 10 twos and target 15 there are 8 answers: k twos and 15 - 2k ones, k = 0..7."
