import random

import pytest

from solution import combination_sum


def norm(result):
    return sorted(sorted(c) for c in result)


def brute(cands, target):
    out = []

    def go(i, remaining, path):
        if remaining == 0:
            out.append(path)
            return
        if i == len(cands) or remaining < 0:
            return
        go(i, remaining - cands[i], path + [cands[i]])
        go(i + 1, remaining, path)

    go(0, target, [])
    return sorted(sorted(p) for p in out)


@pytest.mark.parametrize("cands, target, want, why", [
    ([2, 3, 6, 7], 7, [[2, 2, 3], [7]], "the example"),
    ([2, 3, 5], 8, [[2, 2, 2, 2], [2, 3, 3], [3, 5]], "a number may be used several times"),
    ([4, 6], 3, [], "every candidate is bigger than the target"),
    ([7, 3, 2], 7, [[2, 2, 3], [7]], "unsorted input gives the same combinations"),
    ([2], 1, [], "the only candidate does not fit"),
    ([3], 9, [[3, 3, 3]], "the same number three times"),
])
def test_cases(cands, target, want, why):
    got = combination_sum(list(cands), target)
    assert norm(got) == want, (
        f"combination_sum({cands}, {target}) should be {want} ({why}), got {norm(got)}. "
        "If a combination is missing, check that you recurse with i (reuse allowed).")


def test_no_repeated_multisets():
    got = combination_sum([2, 3, 6, 7], 12)
    keys = [tuple(sorted(c)) for c in got]
    assert len(keys) == len(set(keys)), (
        "The same combination appears more than once in a different order. Never go back to an earlier candidate: "
        "loop from `start`, not from 0.")
    assert norm(got) == brute([2, 3, 6, 7], 12), "combination_sum([2, 3, 6, 7], 12) has the wrong combinations."


def test_random_against_brute_force():
    rng = random.Random(21)
    for _ in range(40):
        cands = rng.sample(range(2, 15), rng.randint(1, 5))
        target = rng.randint(1, 25)
        got = combination_sum(list(cands), target)
        want = brute(sorted(cands), target)
        assert norm(got) == want, f"combination_sum({cands}, {target}) should give {want}, got {norm(got)}."
        assert all(sum(c) == target for c in got), "Every combination must add up to the target."


def test_bigger():
    got = combination_sum(list(range(2, 41)), 40)
    want = brute(list(range(2, 41)), 40)
    assert len(got) == len(want), f"With candidates 2..40 and target 40 there are {len(want)} combinations, got {len(got)}."
