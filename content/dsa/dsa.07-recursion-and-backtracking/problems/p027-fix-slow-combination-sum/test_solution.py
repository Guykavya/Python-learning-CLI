import random

import pytest

from solution import combination_sum


class TooManyCalls(Exception):
    pass


class Counter:
    """Counts the calls of go(); stops the search when there are far too many."""

    def __init__(self, limit=10 ** 7):
        self.calls = 0
        self.limit = limit

    def tick(self):
        self.calls += 1
        if self.calls > self.limit:
            raise TooManyCalls(f"more than {self.limit} calls")


def norm(result):
    return sorted(sorted(c) for c in result)


@pytest.mark.parametrize("cands, target, want", [
    ([2, 3, 6, 7], 7, [[2, 2, 3], [7]]),
    ([2, 3, 5], 8, [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
    ([4, 6], 3, []),
    ([7, 3, 2], 7, [[2, 2, 3], [7]]),
])
def test_answers(cands, target, want):
    counter = Counter()
    got = combination_sum(list(cands), target, counter)
    assert norm(got) == want, (
        f"combination_sum({cands}, {target}) should be {want}, got {norm(got)}. "
        "The fix must not change the answers: did you break before sorting, or change go(i, ...) to go(i + 1, ...)?")
    assert counter.calls >= 1, "counter.tick() was never called. Keep it as the first line of go()."


def test_counter_still_used():
    counter = Counter()
    combination_sum([2, 3, 6, 7], 7, counter)
    assert counter.calls >= 4, "counter.tick() must run once per call of go(). Keep it as the first line of go()."


def test_small_case_is_pruned():
    counter = Counter()
    got = combination_sum([2, 3, 6, 7], 7, counter)
    assert norm(got) == [[2, 2, 3], [7]]
    assert counter.calls <= 12, (
        f"combination_sum([2, 3, 6, 7], 7) made {counter.calls} calls; a pruned search needs 10 (the starter makes 28). "
        "Check candidates[i] > remaining BEFORE recursing, not after.")


def test_big_case_needs_pruning():
    cands = [2, 3] + list(range(41, 90, 2))
    random.Random(27).shuffle(cands)
    counter = Counter(limit=20000)
    try:
        got = combination_sum(list(cands), 120, counter)
    except TooManyCalls:
        raise AssertionError(
            "More than 20,000 calls for candidates [2, 3, 41, 43, ..., 89] and target 120 (a pruned search needs "
            "about 12,000; the starter needs 207,884). Sort the candidates and break as soon as one is bigger than "
            "the remaining target, before making the call.") from None
    assert len(got) == 568, f"There are 568 combinations for target 120, got {len(got)}."
    keys = {tuple(sorted(c)) for c in got}
    assert len(keys) == 568, "Some combinations appear twice."
    assert all(sum(c) == 120 and all(x in cands for x in c) for c in got), "Every combination must use candidates and add up to 120."
