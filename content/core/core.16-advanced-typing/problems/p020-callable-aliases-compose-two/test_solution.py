from collections.abc import Callable
from typing import TypeVar, get_args, get_origin, get_type_hints

import solution
from solution import apply_all, compose_two, count_matching


def norm(t):
    """Unwrap a `type X = ...` alias so both spellings compare equal."""
    return getattr(t, "__value__", t)


def test_aliases_exist_and_are_callables():
    for name, expected in (
        ("IntTransform", ([int], int)),
        ("IntPredicate", ([int], bool)),
    ):
        assert hasattr(solution, name), f"Define the alias {name} at module level."
        alias = norm(getattr(solution, name))
        assert get_origin(alias) is get_origin(Callable[[int], int]), (
            f"{name} must be a Callable type, e.g. Callable[[int], int]."
        )
        assert get_args(alias) == expected, (
            f"{name} should be Callable[[int], {expected[1].__name__}]: parameter types in a list, then the return type."
        )


def test_aliases_used_in_hints():
    h = get_type_hints(count_matching)
    assert h["items"] == list[int] and h["return"] is int, "count_matching(items: list[int], pred: IntPredicate) -> int."
    assert norm(h["pred"]) == Callable[[int], bool], "The pred parameter is an IntPredicate: Callable[[int], bool]."
    h = get_type_hints(apply_all)
    assert h["x"] is int and h["return"] is int, "apply_all(x: int, steps: list[IntTransform]) -> int."
    steps = h["steps"]
    assert get_origin(steps) is list, "steps is a list of transforms: list[IntTransform]."
    assert norm(get_args(steps)[0]) == Callable[[int], int], "Each step is a Callable[[int], int]."


def test_compose_two_uses_three_typevars_consistently():
    h = get_type_hints(compose_two)
    f_params, f_ret = get_args(h["f"])
    g_params, g_ret = get_args(h["g"])
    r_params, r_ret = get_args(h["return"])
    assert get_origin(h["return"]) is get_origin(Callable[[int], int]), (
        "compose_two returns a function, so its return hint is Callable[[A], C]."
    )
    for t in (f_params[0], f_ret, g_params[0], g_ret, r_params[0], r_ret):
        assert isinstance(t, TypeVar), "compose_two must use TypeVars (A, B, C), not int/str/Any."
    a, b, c = f_params[0], f_ret, g_ret
    assert g_params[0] is b, "What f returns (B) is what g accepts: g: Callable[[B], C]."
    assert r_params[0] is a, "The composed function takes what f takes (A): Callable[[A], C]."
    assert r_ret is c, "The composed function returns what g returns (C)."
    assert len({a, b, c}) == 3, "A, B and C are three different TypeVars (f may change the type)."


def test_count_matching():
    assert count_matching([1, 2, 3, 4], lambda n: n % 2 == 0) == 2, "Count items where pred(item) is true."
    assert count_matching([], lambda n: True) == 0, "An empty list has no matches: 0."
    assert count_matching([5, 6], lambda n: n > 100) == 0, "No item matches: 0."


def test_apply_all():
    assert apply_all(3, [lambda n: n + 1, lambda n: n * 2]) == 8, "Apply the steps in order: (3 + 1) * 2 = 8."
    assert apply_all(3, [lambda n: n * 2, lambda n: n + 1]) == 7, "Order matters: (3 * 2) + 1 = 7."
    assert apply_all(9, []) == 9, "No steps: return x unchanged."


def test_compose_two_behaviour():
    h = compose_two(len, lambda n: n * 10)
    assert h("abc") == 30, "compose_two(f, g)(x) is g(f(x)): len('abc') = 3, then 3 * 10."
    assert compose_two(lambda n: n + 1, str)(4) == "5", "First f (4 -> 5), then g (5 -> '5')."
    assert compose_two(str.upper, str.split)("a b") == ["A", "B"], "f then g: 'A B' then ['A', 'B']."


def test_compose_two_order_and_calls():
    calls = []

    def f(x):
        calls.append("f")
        return x

    def g(x):
        calls.append("g")
        return x

    composed = compose_two(f, g)
    assert calls == [], "compose_two must not call f or g yet; it returns a function that will."
    composed(1)
    assert calls == ["f", "g"], "f runs first, then g."
