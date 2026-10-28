import inspect
import typing
from collections.abc import Iterable
from typing import get_args, get_origin, get_type_hints

import solution
from solution import fixed, format_all, percent


def formatter_signature():
    f = getattr(solution, "Formatter", None)
    assert f is not None, "Define the protocol class Formatter."
    assert typing.is_protocol(f), "Formatter must inherit from Protocol."
    assert typing.get_protocol_members(f) == frozenset({"__call__"}), "Formatter has one member: the method __call__."
    sig = inspect.signature(f.__call__)
    params = list(sig.parameters.values())[1:]  # drop self
    return f, params


def test_formatter_signature():
    f, params = formatter_signature()
    assert [p.name for p in params] == ["value", "precision"], "__call__(self, value: float, *, precision: int = 2) -> str."
    assert params[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD, "value is an ordinary parameter."
    assert params[1].kind is inspect.Parameter.KEYWORD_ONLY, "precision comes after a bare * so it is keyword-only."
    assert params[1].default == 2, "precision has the default 2."
    assert get_type_hints(f.__call__) == {"value": float, "precision": int, "return": str}, "Hints: value: float, precision: int, -> str."


def test_functions_have_the_same_signature_as_the_protocol():
    _, params = formatter_signature()
    for fn in (fixed, percent):
        ps = list(inspect.signature(fn).parameters.values())
        assert [(p.name, p.kind, p.default) for p in ps] == [(p.name, p.kind, p.default) for p in params], (
            f"{fn.__name__} must have the same parameters as Formatter.__call__: (value, *, precision=2). Is precision keyword-only?"
        )
        assert get_type_hints(fn) == {"value": float, "precision": int, "return": str}, f"{fn.__name__}: value: float, precision: int, -> str."


def test_format_all_hints():
    h = get_type_hints(format_all)
    assert get_origin(h["values"]) is Iterable and get_args(h["values"]) == (float,), "values: Iterable[float]."
    assert h["fmt"] is solution.Formatter, "fmt: Formatter (your protocol)."
    assert h["precision"] is int and h["return"] == list[str], "precision: int, -> list[str]."


def test_fixed():
    assert fixed(3.14159) == "3.14", "Default precision is 2 digits."
    assert fixed(3.14159, precision=0) == "3", "precision=0: no decimal point at all."
    assert fixed(2, precision=3) == "2.000", "An int is fine; pad with zeros."
    assert fixed(-0.5, precision=1) == "-0.5", "Negative numbers keep their sign."


def test_percent():
    assert percent(0.256) == "25.60%", "Multiply by 100, 2 digits, then add %."
    assert percent(0.256, precision=0) == "26%", "precision=0: '26%'."
    assert percent(1) == "100.00%", "1 is 100%."


def test_format_all_with_functions():
    assert format_all([1, 2.5], fixed) == ["1.00", "2.50"], "Apply fmt to every value."
    assert format_all([0.5, 0.123], percent, precision=1) == ["50.0%", "12.3%"], "format_all passes its precision on to fmt."
    assert format_all([], fixed) == [], "No values: empty list."


def test_format_all_passes_precision_as_keyword():
    calls = []

    def spy(value, *, precision=2):
        calls.append((value, precision))
        return "x"

    assert format_all([1.0, 2.0], spy, precision=5) == ["x", "x"], "One result per value."
    assert calls == [(1.0, 5), (2.0, 5)], "Call fmt(v, precision=precision): keyword form, and use the precision given to format_all."


def test_format_all_with_a_callable_object():
    class Brackets:
        def __call__(self, value, *, precision=2):
            return "[" + fixed(value, precision=precision) + "]"

    assert format_all([1], Brackets()) == ["[1.00]"], "Any object with a matching __call__ is a Formatter."
