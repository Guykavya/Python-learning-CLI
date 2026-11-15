import subprocess
import sys
from pathlib import Path

import pytest

from solution import has_subset_sum

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


@pytest.mark.parametrize("nums, target, want, why", [
    ([3, 34, 4, 12, 5, 2], 9, True, "4 + 5 = 9 (the example)"),
    ([3, 34, 4, 12, 5, 2], 30, False, "no subset sums to 30"),
    ([], 0, True, "the empty subset has sum 0"),
    ([], 5, False, "nothing to choose from"),
    ([5], 5, True, "one item equal to the target"),
    ([1, 2], 0, True, "target 0 is always reachable with the empty subset"),
    ([2, 4, 6], 5, False, "only even sums are possible"),
    ([-3, 1, 7], 4, True, "-3 + 7 = 4: a negative number is needed"),
    ([5, -2], 3, True, "5 + (-2) = 3: do not prune when the sum goes above the target"),
    ([-3, -1], -4, True, "a negative target"),
    ([7, -7, 3], 0, True, "the empty subset, or 7 + (-7)"),
    ([1, 1, 1], 4, False, "the sum of everything is only 3"),
])
def test_cases(nums, target, want, why):
    got = has_subset_sum(list(nums), target)
    assert got is want, f"has_subset_sum({nums}, {target}) should be {want}: {why}."


def test_no_answer_18_items():
    nums = [2 * i for i in range(1, 19)]
    assert has_subset_sum(nums, 101) is False, "18 even numbers can never make the odd number 101."


def test_stops_early():
    code = "from solution import has_subset_sum\nprint(has_subset_sum([1] * 40, 20), has_subset_sum(list(range(1, 41)), 3))\n"
    out = run_code(code, 20, "Searching 40 items for an answer that exists (there are 2^40 subsets: "
                   "return True as soon as the remaining target is 0, and use `or` so the second branch is skipped)")
    assert out == "True True", (
        f"has_subset_sum([1] * 40, 20) and has_subset_sum(range 1..40, 3) are both True; you printed {out!r}.")
