import dataclasses
from collections.abc import Callable
from typing import Generic, TypeVar, get_args, get_origin, get_type_hints

import pytest

from solution import Pair, swap_tuple


def params():
    ps = getattr(Pair, "__parameters__", ())
    assert len(ps) == 2 and all(isinstance(p, TypeVar) for p in ps), (
        "Pair must have TWO type parameters: class Pair(Generic[A, B])."
    )
    return ps


def test_is_generic_in_two_vars():
    a, b = params()
    assert any(get_origin(x) is Generic for x in Pair.__orig_bases__), "Inherit from Generic[A, B]."
    assert a is not b, "A and B must be two different TypeVars."


def test_field_hints():
    a, b = params()
    assert get_type_hints(Pair) == {"first": a, "second": b}, "The fields are first: A and second: B (the first and second parameter of the class)."


def test_swap_hint():
    a, b = params()
    ret = get_type_hints(Pair.swap)["return"]
    assert get_origin(ret) is Pair, "swap returns a Pair: -> 'Pair[B, A]'."
    assert get_args(ret) == (b, a), "swap exchanges the types too: Pair[B, A]. The order of the two TypeVars must be swapped."


def test_map_first_hint():
    a, b = params()
    h = get_type_hints(Pair.map_first)
    func = h["func"]
    assert get_origin(func) is get_origin(Callable[[int], int]), "func must be a Callable: Callable[[A], C]."
    (args, c) = get_args(func)
    assert list(args) == [a], "func takes the first value, so its argument type is A: Callable[[A], C]."
    assert isinstance(c, TypeVar) and c not in (a, b), "func returns a NEW type: use a third TypeVar C, not A or B."
    assert get_origin(h["return"]) is Pair and get_args(h["return"]) == (c, b), "map_first returns Pair[C, B]: new first type, old second type."


def test_map_second_hint():
    a, b = params()
    h = get_type_hints(Pair.map_second)
    (args, c) = get_args(h["func"])
    assert list(args) == [b], "func takes the second value, so its argument type is B: Callable[[B], C]."
    assert get_args(h["return"]) == (a, c), "map_second returns Pair[A, C]: old first type, new second type."


def test_swap_tuple_hint():
    h = get_type_hints(swap_tuple)
    (a, b) = get_args(h["p"])
    assert isinstance(a, TypeVar) and isinstance(b, TypeVar) and a is not b, "p: tuple[A, B] with two different TypeVars."
    assert get_args(h["return"]) == (b, a), "The result is tuple[B, A]."


def test_swap():
    assert Pair("age", 41).swap() == Pair(41, "age"), "swap exchanges first and second."
    assert Pair(1, 2).swap().swap() == Pair(1, 2), "Swapping twice gives the original."


def test_map_first_and_second():
    assert Pair("age", 41).map_first(str.upper) == Pair("AGE", 41), "map_first applies func to the first value only."
    assert Pair("age", 41).map_second(float) == Pair("age", 41.0), "map_second applies func to the second value only."
    assert Pair(1, 2).map_first(lambda x: [x]).first == [1], "The new first value may have a completely different type."


def test_methods_return_new_pairs():
    p = Pair(1, 2)
    q = p.swap()
    assert p == Pair(1, 2) and q is not p, "Do not change self: return a new Pair."
    assert isinstance(q, Pair), "The result is a Pair."


def test_frozen_dataclass():
    assert dataclasses.is_dataclass(Pair), "Pair must be a @dataclass."
    p = Pair(1, 2)
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.first = 5
    assert hash(Pair(1, 2)) == hash(Pair(1, 2)), "frozen=True with eq makes the pair hashable."


def test_swap_tuple():
    assert swap_tuple((1, "x")) == ("x", 1), "Return the tuple with the two items exchanged."
    assert swap_tuple((None, 0)) == (0, None), "Do not rely on truthiness."
