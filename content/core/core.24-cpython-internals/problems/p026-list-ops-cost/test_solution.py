"""Timing tests use RATIOS only (never absolute times) and the best of several repeats,
so they pass on a slow or busy machine."""

import time
from collections import deque

import pytest

from solution import (
    classify,
    growth_kind,
    measure,
    push_pop_end,
    push_pop_front,
    push_pop_left,
    search_missing,
    time_per_call,
)


# ------------------------------------------------------------------ the operations
def test_operations_keep_the_container_unchanged():
    for op, factory in [(push_pop_end, list), (push_pop_front, list), (push_pop_left, deque)]:
        c = factory(range(10))
        op(c)
        op(c)
        assert list(c) == list(range(10)), (
            f"{op.__name__} must leave the container exactly as it found it (add one item, then remove it "
            "from the same end), so every timed call works on a container of the same size n."
        )


def test_push_pop_front_works_at_the_front():
    c = [1, 2, 3]
    seen = []

    class Spy(list):
        def insert(self, index, value):
            seen.append(("insert", index))
            super().insert(index, value)

        def pop(self, *index):
            seen.append(("pop",) + index)
            return super().pop(*index)

    push_pop_front(Spy(c))
    assert seen == [("insert", 0), ("pop", 0)], "push_pop_front must call insert(0, ...) and then pop(0)."


def test_search_missing():
    assert search_missing(list(range(100))) is False, "search_missing looks for -1, which is never in range(n)."
    assert search_missing({1, 2, -1}) is True, "Return the result of the `in` test."


# ------------------------------------------------------------------ growth_kind (no timing)
def test_growth_kind_constant():
    assert growth_kind(1.0e-7, 1.1e-7) == "constant", "About the same time at both sizes: constant."
    assert growth_kind(2.0e-7, 1.0e-7) == "constant", "Faster at the large size (noise) is still constant."


def test_growth_kind_linear():
    assert growth_kind(1.0e-7, 1.0e-5) == "linear", "100 times slower at the large size: linear."


def test_growth_kind_threshold():
    assert growth_kind(1.0, 5.0) == "linear", "The rule is 'at least threshold times slower': 5.0x is linear."
    assert growth_kind(1.0, 4.9) == "constant", "4.9x is below the default threshold of 5."
    assert growth_kind(1.0, 3.0, threshold=2.0) == "linear", "Use the threshold argument, not a fixed 5."


# ------------------------------------------------------------------ time_per_call
def test_time_per_call_builds_container_once():
    ids, sizes = set(), set()

    def op(container):
        ids.add(id(container))
        sizes.add(len(container))

    time_per_call(op, 50, number=10, repeat=3)
    assert len(ids) == 1, (
        "Build the container ONCE, before timing, and time only op(container). Building it inside the "
        "timed code measures list(range(n)) instead of the operation."
    )
    assert sizes == {50}, "The container must have n items: factory(range(n))."


def test_time_per_call_uses_factory():
    kinds = set()
    time_per_call(lambda c: kinds.add(type(c)), 5, factory=deque, number=3, repeat=2)
    assert kinds == {deque}, "Create the container with factory(range(n))."


def test_time_per_call_is_per_call():
    few = time_per_call(search_missing, 10_000, number=10, repeat=5)
    many = time_per_call(search_missing, 10_000, number=100, repeat=5)
    assert 0.3 < many / few < 3, (
        "time_per_call must return seconds for ONE call: divide the total by number. "
        "Ten times more calls should not give a ten times larger result."
    )


def test_time_per_call_takes_the_best_repeat():
    calls = [0]

    def op(container):
        calls[0] += 1
        if calls[0] <= 5:          # the whole first repeat is slow (as if the machine were busy)
            time.sleep(0.006)

    per_call = time_per_call(op, 10, number=5, repeat=3)
    assert calls[0] == 15, "Run `repeat` timings of `number` calls each (timeit.repeat does this)."
    assert per_call < 0.001, (
        "Return the BEST (min) of the repeats, not the first or the average: a slow repeat means the "
        "machine was busy, never that the code got faster."
    )


def test_measure_returns_dict():
    result = measure(push_pop_end, [10, 100], number=20, repeat=2)
    assert set(result) == {10, 100}, "measure returns {n: seconds per call} for each size."
    assert all(isinstance(t, float) and t > 0 for t in result.values()), "Each value is a positive float."


# ------------------------------------------------------------------ real measurements (ratios only)
def test_append_pop_is_constant():
    assert classify(push_pop_end, list, repeat=7) == "constant", (
        "append() and pop() at the END of a list are amortised O(1). If you got 'linear', check that the "
        "list is built outside the timed code and that you take the best of the repeats."
    )


def test_insert0_pop0_is_linear():
    assert classify(push_pop_front, list, number=50) == "linear", (
        "insert(0, x) and pop(0) shift every element of the array: O(n). 100x more items should be far slower."
    )


def test_deque_front_is_constant():
    assert classify(push_pop_left, deque, repeat=7) == "constant", (
        "deque.appendleft/popleft are O(1): a deque is a linked list of blocks, nothing is shifted."
    )


def test_search_list_is_linear_but_set_is_constant():
    assert classify(search_missing, list, number=20, repeat=3) == "linear", (
        "`x in list` compares x with every item until it finds it: a missing item costs n comparisons."
    )
    assert classify(search_missing, set, repeat=7) == "constant", (
        "`x in set` hashes x and looks in one slot of the hash table: O(1) on average."
    )
