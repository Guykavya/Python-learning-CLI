from collections.abc import Sequence
from typing import TypeVar, get_args, get_origin, get_type_hints

import pytest

from solution import first, first_or, last_or_none


def seq_arg(hint, who):
    assert get_origin(hint) in (Sequence, list), (
        f"{who}: the parameter must be Sequence[T] (a Sequence of the TypeVar), not {hint!r}."
    )
    (arg,) = get_args(hint)
    assert isinstance(arg, TypeVar), f"{who}: the item type inside Sequence[...] must be a TypeVar, not {arg!r}. Plain int/object/Any loses the link to the result."
    return arg


def test_first_hints():
    h = get_type_hints(first)
    t = seq_arg(h["items"], "first")
    assert h["return"] is t, "first must return the SAME TypeVar that is inside Sequence[...]: items: Sequence[T] -> T."


def test_first_or_hints():
    h = get_type_hints(first_or)
    t = seq_arg(h["items"], "first_or")
    assert h["default"] is t, "The default is also an item, so it must be the same TypeVar: default: T."
    assert h["return"] is t, "first_or returns an item or the default: both are T, so -> T."


def test_last_or_none_hints():
    h = get_type_hints(last_or_none)
    t = seq_arg(h["items"], "last_or_none")
    assert set(get_args(h["return"])) == {t, type(None)}, "last_or_none may return an item or None: -> T | None, using the same T."


def test_first():
    assert first([3, 4]) == 3, "first([3, 4]) is 3."
    assert first("abc") == "a", "A str is a Sequence of str: first('abc') is 'a'."
    assert first((None, 1)) is None, "None is a real item here. Do not test the item for truthiness."


def test_first_empty_raises():
    with pytest.raises(IndexError):
        first([])


def test_first_or():
    assert first_or([5, 6], 0) == 5, "A non-empty sequence ignores the default."
    assert first_or([], 0) == 0, "An empty sequence gives the default."
    assert first_or([0, 1], 9) == 0, "0 is falsy but it is a real item: test len(items) == 0, not 'if not items[0]'."
    assert first_or("", "?") == "?", "An empty str is an empty Sequence."


def test_last_or_none():
    assert last_or_none((1, 2, 3)) == 3, "The last item is items[-1]."
    assert last_or_none([]) is None, "An empty sequence has no last item: None."
    assert last_or_none([0]) == 0, "0 is a real item, not 'nothing'."
    assert last_or_none("xyz") == "z", "It works for any Sequence, a str too."
