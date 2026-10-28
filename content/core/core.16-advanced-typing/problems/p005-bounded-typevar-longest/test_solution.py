from collections.abc import Iterable, Sized
from typing import TypeVar, get_args, get_origin, get_type_hints

import pytest

from solution import longest, longest_or_none, shortest


def check_hint(func, returns_optional=False):
    h = get_type_hints(func)
    name = func.__name__
    assert get_origin(h["items"]) is Iterable, f"{name}: items must be Iterable[S] (any iterable, even an iterator)."
    (s,) = get_args(h["items"])
    assert isinstance(s, TypeVar), f"{name}: the item type must be a TypeVar, not {s!r}."
    bound = s.__bound__
    assert bound is not None, f"{name}: the TypeVar needs a bound, TypeVar('S', bound=Sized). Without it len(item) is an error for the checker."
    assert isinstance(bound, type) and issubclass(bound, Sized), f"{name}: the bound must be Sized (anything with __len__), not {bound!r}."
    if returns_optional:
        assert set(get_args(h["return"])) == {s, type(None)}, f"{name}: returns an item or None: -> S | None."
    else:
        assert h["return"] is s, f"{name}: must return the SAME TypeVar as the items: Iterable[S] -> S."
    return s


def test_hints():
    s1 = check_hint(longest)
    s2 = check_hint(shortest)
    s3 = check_hint(longest_or_none, returns_optional=True)
    assert s1.__bound__ is s2.__bound__ is s3.__bound__, "Use the same bound everywhere."


def test_longest():
    assert longest(["a", "abc", "ab"]) == "abc", "Return the item with the largest len."
    assert longest([[1], [2, 3], [4]]) == [2, 3], "It works for lists too: anything with a len."
    assert longest([(), (1,)]) == (1,), "It works for tuples."
    assert longest([{"a": 1, "b": 2}, {"c": 3}]) == {"a": 1, "b": 2}, "Dicts have a len as well."


def test_longest_tie_returns_first():
    a, b = [1, 2], [3, 4]
    assert longest([a, b]) is a, "On a tie return the FIRST item: replace the best only if strictly longer (>, not >=)."
    assert longest(["aa", "bb", "cc"]) == "aa", "Three-way tie: the first one."


def test_shortest():
    assert shortest(["bb", "a", "c"]) == "a", "Return the item with the smallest len."
    c, d = [1], [2]
    assert shortest([c, d]) is c, "On a tie return the FIRST item (< not <=)."
    assert shortest([""]) == "", "A single empty item is the answer."


def test_works_with_iterators():
    assert longest(iter(["xy", "z"])) == "xy", "items may be a one-shot iterator: walk it only once, do not call len(items) or index it."
    assert shortest(x for x in ["xy", "z", "w"]) == "z", "A generator is an Iterable too."


def test_empty():
    with pytest.raises(ValueError, match="longest"):
        longest([])
    with pytest.raises(ValueError, match="shortest"):
        shortest([])


def test_longest_or_none():
    assert longest_or_none([]) is None, "An empty input gives None."
    assert longest_or_none(["", "a"]) == "a", "Otherwise it is longest()."
    assert longest_or_none([""]) == "", "An empty string is a real item, not 'nothing': do not test the result for truthiness."
    assert longest_or_none(iter([])) is None, "An empty iterator gives None."
