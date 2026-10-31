import math

import pytest

from solution import first_bad


class Checker:
    """An is_bad that counts its calls and refuses versions that are not in the list."""

    def __init__(self, versions, first_bad_index):
        self.versions = versions
        self.position = {v: i for i, v in enumerate(versions)}
        self.first = first_bad_index
        self.calls = 0

    def __call__(self, v):
        assert v in self.position, f"is_bad was called with {v!r}, which is not one of the versions."
        self.calls += 1
        return self.position[v] >= self.first


def limit(n):
    return math.ceil(math.log2(n)) + 1 if n > 0 else 0


def test_example():
    versions = [f"v{i}" for i in range(1, 9)]
    check = Checker(versions, 5)
    assert first_bad(versions, check) == "v6", "v6 is the first version where is_bad is True."
    assert check.calls <= limit(8), f"{check.calls} calls for 8 versions; the limit is {limit(8)}."


def test_none_bad_returns_none():
    versions = list(range(100))
    check = Checker(versions, 100)
    assert first_bad(versions, check) is None, "No version is bad: return None."
    assert check.calls <= limit(100), (
        f"{check.calls} calls when nothing is bad; limit {limit(100)}. Let hi = n stand for 'none'."
    )


def test_all_bad_returns_first():
    versions = list(range(100))
    check = Checker(versions, 0)
    assert first_bad(versions, check) == 0, "Every version is bad: the first one (index 0) is the answer."
    assert check.calls <= limit(100), f"{check.calls} calls; limit {limit(100)}."


def test_empty_list():
    check = Checker([], 0)
    assert first_bad([], check) is None, "No versions: return None."
    assert check.calls == 0, "With no versions, do not call is_bad at all."


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 7, 8, 9, 16, 17])
def test_every_position_small_lists(n):
    versions = [f"c{i:03}" for i in range(n)]
    for first in range(n + 1):
        check = Checker(versions, first)
        expected = versions[first] if first < n else None
        got = first_bad(versions, check)
        assert got == expected, (
            f"n={n}, first bad at index {first}: expected {expected!r}, got {got!r}. "
            + ("Nothing is bad here: your search must be able to answer None (let hi = n mean 'none')."
               if expected is None else
               "Check how lo and hi move: if mid is bad it can still be the answer (hi = mid).")
        )
        assert check.calls <= limit(n), (
            f"n={n}, first bad at index {first}: {check.calls} calls, limit {limit(n)}."
        )


def test_thousand_commits_need_few_calls():
    versions = [f"commit-{i:04}" for i in range(1000)]
    for first in (0, 1, 499, 500, 731, 998, 999, 1000):
        check = Checker(versions, first)
        expected = versions[first] if first < 1000 else None
        assert first_bad(versions, check) == expected, f"Wrong answer for first bad index {first}."
        assert check.calls <= 11, (
            f"{check.calls} calls of is_bad for 1000 versions. Bisection needs at most 11: "
            "test the middle and throw away the half that cannot contain the answer."
        )


def test_does_not_change_the_list():
    versions = [3, 1, 2]  # order is history order, not sorted order
    snapshot = list(versions)
    first_bad(versions, lambda v: v == 2)
    assert versions == snapshot, "Do not sort or change the versions list: its order IS the history."
