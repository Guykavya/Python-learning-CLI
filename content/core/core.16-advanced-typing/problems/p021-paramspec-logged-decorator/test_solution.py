import inspect
from collections.abc import Callable
from typing import ParamSpec, TypeVar, get_args, get_origin, get_type_hints

import pytest

import solution
from solution import CALL_LOG, logged, logged_as

CALLABLE = get_origin(Callable[[int], int])


@pytest.fixture(autouse=True)
def clear_log():
    CALL_LOG.clear()
    yield
    CALL_LOG.clear()


def make_functions():
    @logged
    def add(a, b):
        return a + b

    @logged
    def greet(name, punctuation="."):
        return f"Hello {name}{punctuation}"

    return add, greet


def test_call_log_is_a_list_of_str():
    assert get_type_hints(solution)["CALL_LOG"] == list[str], "CALL_LOG: list[str] = []"
    assert solution.CALL_LOG is CALL_LOG, "Keep one module-level CALL_LOG list; do not rebind it."


def test_logged_hints_use_paramspec():
    h = get_type_hints(logged)
    assert get_origin(h["func"]) is CALLABLE, "func is a Callable[P, R]."
    p, r = get_args(h["func"])
    assert isinstance(p, ParamSpec), "The parameters of func are a ParamSpec (P = ParamSpec('P')), not [...] or Any."
    assert isinstance(r, TypeVar), "The result of func is a TypeVar (R = TypeVar('R'))."
    assert get_origin(h["return"]) is CALLABLE and get_args(h["return"]) == (p, r), (
        "logged returns Callable[P, R]: the same P and R, so the signature survives decoration."
    )


def test_logged_as_hints():
    h = get_type_hints(logged_as)
    assert h["prefix"] is str, "prefix: str."
    ret = h["return"]
    assert get_origin(ret) is CALLABLE, "logged_as returns a decorator: Callable[[Callable[P, R]], Callable[P, R]]."
    params, inner = get_args(ret)
    assert isinstance(params, list) and len(params) == 1, "The decorator takes exactly one argument, the function."
    assert get_origin(params[0]) is CALLABLE and get_args(params[0]) == get_args(inner), (
        "The decorator takes Callable[P, R] and returns the same Callable[P, R]."
    )
    p, r = get_args(inner)
    assert isinstance(p, ParamSpec) and isinstance(r, TypeVar), "Use P (ParamSpec) and R (TypeVar) inside."


def test_result_and_log_positional():
    add, _ = make_functions()
    assert add(1, 2) == 3, "The decorated function must still return the original result."
    assert CALL_LOG == ["add(1, 2)"], "Log 'name(args)' with repr of each argument."


def test_log_keywords_and_repr():
    _, greet = make_functions()
    assert greet("Ada", punctuation="!") == "Hello Ada!", "Pass keyword arguments through unchanged."
    assert CALL_LOG == ["greet('Ada', punctuation='!')"], (
        "Use repr for values ('Ada' with quotes) and write keywords as name=value after the positional ones."
    )


def test_log_order_and_no_args():
    @logged
    def ping():
        return "pong"

    add, _ = make_functions()
    ping()
    add(5, 6)
    add(1, b=5)
    assert CALL_LOG == ["ping()", "add(5, 6)", "add(1, b=5)"], "One entry per call, in call order; no arguments gives '()'."


def test_logged_before_the_call_even_if_it_raises():
    @logged
    def boom(x):
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        boom(3)
    assert CALL_LOG == ["boom(3)"], "Append the log line before calling the function, so failing calls are logged too."


def test_wraps_keeps_name_doc_and_signature():
    @logged
    def area(width: int, height: int = 2) -> int:
        """Rectangle area."""
        return width * height

    assert area.__name__ == "area", "Use functools.wraps so __name__ is kept."
    assert area.__doc__ == "Rectangle area.", "functools.wraps also keeps the docstring."
    assert inspect.signature(area) == inspect.signature(area.__wrapped__), "wraps sets __wrapped__ so the signature is visible."
    assert str(inspect.signature(area)) == "(width: int, height: int = 2) -> int", "The real signature must be visible."


def test_logged_as_prefix():
    @logged_as("db")
    def add(a, b):
        return a + b

    assert add(1, 2) == 3, "logged_as(...) decorated function still returns the result."
    assert CALL_LOG == ["db: add(1, 2)"], "The line starts with 'prefix: '."
    assert add.__name__ == "add", "logged_as must also use functools.wraps."


def test_logged_as_factories_are_independent():
    @logged_as("a")
    def f():
        return 1

    @logged_as("b")
    def g():
        return 2

    f()
    g()
    f()
    assert CALL_LOG == ["a: f()", "b: g()", "a: f()"], "Each factory call keeps its own prefix (a closure)."
