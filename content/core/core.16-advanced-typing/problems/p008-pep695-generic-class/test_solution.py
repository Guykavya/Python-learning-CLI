from collections.abc import Callable
from typing import TypeVar, get_args, get_origin, get_type_hints

from solution import Box, biggest


def test_box_uses_new_syntax():
    tp = getattr(Box, "__type_params__", ())
    assert len(tp) == 1, "Write class Box[T]: the new syntax puts one type parameter in brackets after the class name (Box.__type_params__ must have one entry)."
    assert tp[0].__name__ == "T", "Name the type parameter T."


def test_box_hints():
    (t,) = Box.__type_params__
    assert get_type_hints(Box.__init__) == {"value": t, "return": type(None)}, "__init__(self, value: T) -> None."
    assert get_type_hints(Box.get) == {"return": t}, "get returns the stored value: -> T."


def test_map_has_its_own_type_parameter():
    (t,) = Box.__type_params__
    tp = getattr(Box.map, "__type_params__", ())
    assert len(tp) == 1, "map needs its own type parameter: def map[U](self, func: ...) -> ..."
    (u,) = tp
    assert u is not t, "U must be a new parameter, different from T."
    h = get_type_hints(Box.map)
    func = h["func"]
    assert get_origin(func) is get_origin(Callable[[int], int]), "func: Callable[[T], U]."
    (args, ret) = get_args(func)
    assert list(args) == [t] and ret is u, "func takes the box's T and returns the new type U: Callable[[T], U]."
    assert get_origin(h["return"]) is Box and get_args(h["return"]) == (u,), "map returns a Box[U], a box of the NEW type."


def test_biggest_has_constraints():
    tp = getattr(biggest, "__type_params__", ())
    assert len(tp) == 1, "Write biggest[N: (int, float)](a, b): one type parameter."
    (n,) = tp
    assert n.__constraints__ == (int, float), "N must be constrained to exactly (int, float): [N: (int, float)]."
    h = get_type_hints(biggest)
    assert h == {"a": n, "b": n, "return": n}, "a, b and the result all have the type N."


def test_box_behaviour():
    b = Box(5)
    assert b.get() == 5 and b.value == 5, "get() returns the value, also stored as .value."
    assert repr(Box("x")) == "Box('x')" and repr(Box(5)) == "Box(5)", "repr is Box(<repr of the value>)."


def test_map():
    b = Box(5)
    m = b.map(str)
    assert m == Box("5") and isinstance(m, Box), "map returns a new Box holding func(value)."
    assert b.get() == 5 and m is not b, "map must not change the original box."
    assert b.map(lambda n: n * 2).map(lambda n: n + 1).get() == 11, "map can be chained."
    assert Box(None).map(lambda x: x is None).get() is True, "None is a perfectly good value."


def test_equality_and_hash():
    assert Box(1) == Box(1), "Boxes with equal values are equal."
    assert Box(1) != Box(2), "Different values: not equal."
    assert Box(1) != 1, "A Box is not equal to its bare value."
    assert (Box(1) == 1) is False, "Return NotImplemented for non-Box: Python then answers False."
    assert len({Box(1), Box(1), Box(2)}) == 2, "Equal boxes must hash equally: define __hash__ when you define __eq__."
    assert hash(Box("a")) == hash(Box("a")), "Same value: same hash."


def test_biggest():
    assert biggest(3, 7) == 7 and biggest(7, 3) == 7, "Return the larger number."
    assert biggest(2.5, 1.0) == 2.5, "It works for floats too."
    a, b = 2, 2.0
    assert biggest(a, b) is a, "On a tie return the first argument (replace only when strictly larger)."
    assert biggest(-1, -2) == -1, "Negative numbers: -1 is larger."
