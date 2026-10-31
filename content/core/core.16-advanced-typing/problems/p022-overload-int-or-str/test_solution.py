from typing import Literal, get_args, get_origin, get_overloads, get_type_hints

import pytest

from solution import double, to_number


def sigs(func):
    return [get_type_hints(o) for o in get_overloads(func)]


def test_double_has_two_overloads():
    found = get_overloads(double)
    assert len(found) == 2, (
        f"double has {len(found)} overloads. Decorate two signatures with @overload "
        "(from typing import overload), each with a '...' body, before the real function."
    )


def test_double_overload_types():
    pairs = {(h["x"], h["return"]) for h in sigs(double)}
    assert pairs == {(int, int), (str, str)}, (
        "The overloads must be double(x: int) -> int and double(x: str) -> str. "
        "Each argument type is paired with the SAME result type."
    )


def test_double_behaviour():
    assert double(21) == 42, "An int is doubled: 21 * 2."
    assert double("ab") == "abab", "A str is repeated twice."
    assert double("") == "", "The empty string doubled is empty."
    assert isinstance(double(3), int) and isinstance(double("a"), str), "int in, int out; str in, str out."


@pytest.mark.parametrize("bad", [2.5, None, [1], (1,)])
def test_double_rejects_other_types(bad):
    with pytest.raises(TypeError):
        double(bad)


def test_to_number_has_two_overloads():
    assert len(get_overloads(to_number)) == 2, "to_number needs two @overload signatures (Literal[True] and Literal[False])."


def test_to_number_overload_types():
    by_return = {}
    for h in sigs(to_number):
        by_return[h["return"]] = h
    assert set(by_return) == {float, int}, "One overload returns float, the other returns int."
    flag_true = by_return[float]["as_float"]
    flag_false = by_return[int]["as_float"]
    assert get_origin(flag_true) is Literal and get_args(flag_true) == (True,), (
        "The float overload has as_float: Literal[True]."
    )
    assert get_origin(flag_false) is Literal and get_args(flag_false) == (False,), (
        "The int overload has as_float: Literal[False] = False."
    )
    assert by_return[float]["text"] is str and by_return[int]["text"] is str, "text: str in both overloads."


def test_default_only_on_the_int_overload():
    import inspect

    for o in get_overloads(to_number):
        sig = inspect.signature(o)
        returns_int = get_type_hints(o)["return"] is int
        has_default = sig.parameters["as_float"].default is not inspect.Parameter.empty
        if returns_int:
            assert has_default and sig.parameters["as_float"].default is False, (
                "The int overload must default as_float to False, so to_number('7') is an int."
            )
        else:
            assert not has_default, (
                "The float overload has no default: a call without the flag must match the int overload."
            )


def test_to_number_behaviour():
    assert to_number("7") == 7 and isinstance(to_number("7"), int), "Default: int('7')."
    assert to_number("7", False) == 7 and isinstance(to_number("7", False), int), "as_float=False gives an int."
    assert to_number("7", True) == 7.0 and isinstance(to_number("7", True), float), "as_float=True gives a float."
    assert to_number("2.5", as_float=True) == 2.5, "Works with the keyword form too."
    assert to_number("-12") == -12, "Negative numbers work."
    with pytest.raises(ValueError):
        to_number("abc")


def test_implementation_is_a_single_real_function():
    assert callable(double) and double.__name__ == "double", "The last (undecorated) def double is the real function."
    assert getattr(double, "__wrapped__", None) is None, "Do not wrap the functions; just define the overloads before them."
