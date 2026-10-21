import ast
from pathlib import Path

from solution import dig

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())


def expect_raise(exc_type, func, *args, match=None, why=""):
    """Call func(*args). It must raise exc_type, with match in its message if match is given."""
    try:
        result = func(*args)
    except exc_type as e:
        if match is not None:
            assert match in str(e), (
                f"The {exc_type.__name__} message should contain {match!r}, but it was {str(e)!r}. {why}")
        return e
    except Exception as e:
        raise AssertionError(
            f"Expected {exc_type.__name__}, but {type(e).__name__} was raised: {e}. {why}") from e
    raise AssertionError(f"Expected {exc_type.__name__}, but the call returned {result!r}. {why}")


def order():
    return {"customer": {"name": "Asha"}, "items": [{"name": "tea", "qty": 2}, {"name": "vada", "qty": 1}]}


def test_found():
    assert dig(order(), ["customer", "name"]) == "Asha"
    assert dig(order(), ["items", 1, "name"]) == "vada", "Follow every key in turn: data = data[key]."
    assert dig(order(), ["items", -1, "qty"]) == 1, "Negative indexes are valid list positions."


def test_missing_key_gives_default():
    assert dig(order(), ["customer", "phone"]) is None, "A missing key is a failed lookup: return default."
    assert dig(order(), ["customer", "phone"], "-") == "-", "Return the default the caller passed."


def test_bad_index_gives_default():
    assert dig(order(), ["items", 5, "qty"], 0) == 0, (
        "An index out of range raises IndexError, which is also a lookup failure. "
        "Catch their common parent, LookupError.")


def test_empty_keys():
    data = order()
    assert dig(data, []) is data, "With no keys, return data itself."


def test_found_value_none_or_falsy():
    assert dig({"a": 0}, ["a"], 99) == 0, "A found value of 0 must be returned, not replaced by the default."
    assert dig({"a": None}, ["a"], 99) is None


def test_type_mismatch_propagates():
    expect_raise(TypeError, dig, order(), ["items", "first"],
                 why="A list indexed with a string is a bug in the path. Do not catch TypeError.")
    expect_raise(TypeError, dig, {"a": 5}, ["a", "b"], why="An int cannot be indexed: TypeError must propagate.")


def test_one_family_clause():
    names = [ast.unparse(h.type) if h.type is not None else "bare"
             for h in ast.walk(TREE) if isinstance(h, ast.ExceptHandler)]
    assert names, "Use try/except around the lookups."
    assert "bare" not in names and "Exception" not in names, "Do not catch everything: TypeError must escape."
