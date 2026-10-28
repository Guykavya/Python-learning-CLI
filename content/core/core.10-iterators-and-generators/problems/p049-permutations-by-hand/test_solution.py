import itertools
import time

import solution
from solution import anagrams, perms


def test_full_permutations():
    assert list(perms([1, 2, 3])) == list(itertools.permutations([1, 2, 3])), (
        "Same tuples in the same order as itertools: take each position in turn as the first item, then recurse on the rest."
    )


def test_with_r():
    for r in range(5):
        assert list(perms("abc", r)) == list(itertools.permutations("abc", r)), f"perms('abc', {r}) must match itertools.permutations."


def test_r_zero_and_too_big():
    assert list(perms("abc", 0)) == [()], "r = 0: exactly one empty arrangement, ()."
    assert list(perms("ab", 3)) == [], "r larger than the number of items: nothing."
    assert list(perms([])) == [()], "No items and r = None (so r = 0): one empty tuple, like itertools."


def test_tuples_not_lists():
    first = next(iter(perms("ab")))
    assert first == ("a", "b") and isinstance(first, tuple), "Yield tuples, not lists or strings."


def test_equal_items_kept_by_position():
    assert list(perms("aa")) == [("a", "a"), ("a", "a")], "Items are chosen by position: two equal letters still give two arrangements."


def test_any_iterable():
    assert list(perms(x for x in "xy")) == [("x", "y"), ("y", "x")], (
        "A generator input can be read only once: store the items in a list at the start."
    )


def test_bigger_matches_itertools():
    assert list(perms(range(5), 3)) == list(itertools.permutations(range(5), 3)), "Order must match for 5 items, r = 3."


def test_lazy_first_item():
    start = time.perf_counter()
    first = next(perms(range(9)))
    elapsed = time.perf_counter() - start
    assert first == tuple(range(9)), "The first arrangement keeps the original order."
    assert elapsed < 0.1, (
        f"The first arrangement took {elapsed:.2f}s. perms must be lazy: use yield / yield from in the "
        "recursion, do not build a list of the smaller arrangements."
    )


def test_no_itertools():
    source = open(solution.__file__, encoding="utf-8").read()
    assert "itertools" not in source, "Build it yourself: do not use itertools in solution.py."


def test_anagrams():
    assert list(anagrams("aab")) == ["aab", "aba", "baa"], "Each different string once, in the order of perms. Join the tuple with ''.join."
    assert list(anagrams("abc")) == ["abc", "acb", "bac", "bca", "cab", "cba"], "All letters different: 6 anagrams."


def test_anagrams_small():
    assert list(anagrams("zz")) == ["zz"], "Equal letters give one string."
    assert list(anagrams("")) == [""], "The empty word has one arrangement: the empty string."
