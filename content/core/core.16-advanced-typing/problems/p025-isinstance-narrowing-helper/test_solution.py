import ast
import inspect
from typing import get_type_hints

import pytest

import solution
from solution import describe, first_text, to_int, total_length


def test_hints_to_int():
    assert get_type_hints(to_int) == {"value": int | str | None, "return": int}, (
        "to_int(value: int | str | None) -> int. The result is always an int, never None."
    )


def test_hints_describe():
    assert get_type_hints(describe) == {"value": int | str | list[int], "return": str}, (
        "describe(value: int | str | list[int]) -> str."
    )


def test_hints_total_length():
    assert get_type_hints(total_length) == {"items": list[str | list[str]], "return": int}, (
        "total_length(items: list[str | list[str]]) -> int."
    )


def test_hints_first_text():
    assert get_type_hints(first_text) == {"values": list[int | str], "return": str | None}, (
        "first_text(values: list[int | str]) -> str | None."
    )


@pytest.mark.parametrize("name", ["to_int", "describe", "total_length", "first_text"])
def test_function_uses_isinstance(name):
    tree = ast.parse(inspect.getsource(getattr(solution, name)))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "isinstance"]
    assert calls, f"{name} should narrow its argument with isinstance(...)."


def test_to_int():
    # "" is a str, not None: int("") raises ValueError. Do not treat empty/falsy values as None.
    assert to_int(None) == 0, "None gives 0."
    assert to_int("12") == 12 and isinstance(to_int("12"), int), "A str is converted with int(...)."
    assert to_int(7) == 7, "An int is returned unchanged."
    assert to_int(0) == 0 and to_int("0") == 0, "0 is a valid int, not 'nothing'."
    assert to_int("-5") == -5, "Negative text works."
    with pytest.raises(ValueError):
        to_int("")
    with pytest.raises(ValueError):
        to_int("abc")


def test_describe():
    assert describe(5) == "int 5", "An int gives 'int 5'."
    assert describe("ab") == "str 'ab'", "A str gives \"str 'ab'\" (repr puts the quotes)."
    assert describe([1, 2, 3]) == "list of 3", "A list gives 'list of N'."
    assert describe([]) == "list of 0", "An empty list is still a list: 'list of 0'."
    assert describe("") == "str ''", "The empty string is a str, not 'nothing'."
    assert describe(0) == "int 0", "0 is an int."


def test_total_length():
    assert total_length(["ab", ["c", "de"]]) == 5, "'ab' is 2, the nested list is 1 + 2."
    assert total_length([]) == 0, "No items: 0."
    assert total_length([[], "x"]) == 1, "An empty nested list adds 0."
    assert total_length(["", ""]) == 0, "Empty strings add 0."
    assert total_length([["abc"]]) == 3, "A nested list of one string adds its length."


def test_first_text():
    assert first_text([1, 2, "x", "y"]) == "x", "The first str, scanning left to right."
    assert first_text([1, 2]) is None, "No str: None."
    assert first_text([]) is None, "An empty list has no str: None."
    assert first_text([3, ""]) == "", "The empty string is still a str: return it, do not skip it."
