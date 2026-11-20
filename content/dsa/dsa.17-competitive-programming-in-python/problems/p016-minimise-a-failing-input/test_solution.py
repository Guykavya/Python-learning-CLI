import random

import pytest

from solution import shrink


def is_one_minimal(res, fails):
    if not fails(res):
        return "the result does not fail any more"
    for i in range(len(res)):
        if fails(res[:i] + res[i + 1:]):
            return f"element {res[i]} at position {i} can still be removed"
    return None


def test_seven_before_three():
    fails = lambda c: 7 in c and 3 in c and c.index(7) < c.index(3)
    assert shrink([5, 7, 1, 9, 3, 3, 8], fails) == [7, 3]


def test_long_list_with_two_culprits():
    rng = random.Random(16)
    case = [rng.choice([1, 2, 4, 5, 6, 8, 9]) for _ in range(40)]
    case[11], case[29] = 7, 3
    fails = lambda c: 7 in c and 3 in c and c.index(7) < c.index(3)
    assert shrink(case, fails) == [7, 3], "Only the 7 and the 3 are needed to fail."


def test_original_is_not_changed():
    case = [4, 8, 15, 16, 23, 42]
    copy = list(case)
    shrink(case, lambda c: 15 in c)
    assert case == copy, "Do not modify the list you receive."


def test_result_is_one_minimal_for_a_sum_predicate():
    rng = random.Random(160)
    for _ in range(20):
        case = [rng.randint(1, 20) for _ in range(30)]
        fails = lambda c: sum(c) > 100
        res = shrink(case, fails)
        why = is_one_minimal(res, fails)
        assert why is None, f"Not 1-minimal: {why}. After a successful removal stay at the same index, and repeat passes."


def test_needs_a_second_pass():
    # Removing 5 first gives [1, 2], which does not fail. After 1 is gone, 5 can be removed too.
    def fails(c):
        return c in ([5, 1, 2], [5, 2], [2])

    res = shrink([5, 1, 2], fails)
    assert res == [2], (
        "One pass leaves [5, 2], but the 5 can go once the 1 is gone. Repeat the pass until nothing changes.")


def test_equal_elements():
    fails = lambda c: c.count(2) >= 2
    assert shrink([2, 1, 2, 3, 2], fails) == [2, 2], "Duplicates: keep exactly two 2s."


def test_not_failing_raises():
    with pytest.raises(ValueError):
        shrink([1, 2, 3], lambda c: False)


def test_number_of_calls():
    calls = [0]
    n = 60

    def fails(c):
        calls[0] += 1
        return 3 in c and 9 in c

    shrink(list(range(n)), fails)
    assert calls[0] <= n * (n + 1) + 2, f"{calls[0]} calls to fails: too many for n = {n}."
