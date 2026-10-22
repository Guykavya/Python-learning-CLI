from collections.abc import Callable
from typing import get_type_hints

from solution import apply_all, compose, keep_if, make_adder

INT_TO_INT = Callable[[int], int]


def test_hints():
    assert get_type_hints(apply_all) == {
        "func": INT_TO_INT,
        "numbers": list[int],
        "return": list[int],
    }, "apply_all(func: Callable[[int], int], numbers: list[int]) -> list[int]."
    assert get_type_hints(keep_if) == {
        "test": Callable[[int], bool],
        "numbers": list[int],
        "return": list[int],
    }, "keep_if's test takes an int and returns a bool: Callable[[int], bool]."
    assert get_type_hints(compose) == {
        "first": INT_TO_INT,
        "second": INT_TO_INT,
        "return": INT_TO_INT,
    }, "compose takes two int -> int functions and returns one: all three are Callable[[int], int]."
    assert get_type_hints(make_adder) == {"n": int, "return": INT_TO_INT}, (
        "make_adder takes an int and returns a function: -> Callable[[int], int]."
    )


def test_apply_all():
    assert apply_all(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6], "Apply func to every number."
    assert apply_all(abs, []) == [], "An empty list stays empty."


def test_keep_if():
    assert keep_if(lambda x: x > 1, [1, 2, 3]) == [2, 3], "Keep numbers where test is True."
    assert keep_if(lambda x: x % 2 == 0, [1, 3]) == [], "No number passes: empty list."


def test_make_adder():
    add3 = make_adder(3)
    assert callable(add3), "make_adder must return a function, not a number."
    assert add3(4) == 7, "make_adder(3)(4) is 7."
    assert make_adder(10)(1) == 11 and add3(0) == 3, "Each adder remembers its own n."


def test_compose_order():
    f = compose(make_adder(1), lambda x: x * 2)
    assert f(5) == 12, "compose(first, second)(x) is second(first(x)): (5 + 1) * 2 = 12."
    g = compose(lambda x: x * 2, make_adder(1))
    assert g(5) == 11, "Apply first, then second: (5 * 2) + 1 = 11."
