from solution import invite
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_calls_without_list_do_not_share():
    first = invite("Asha")
    second = invite("Ravi")
    third = invite("Zoya")
    assert second == ["Ravi"], (
        "The second call returned more than ['Ravi']: every call without a list must start a NEW list. "
        "A default of [] is created once and shared by all calls.")
    assert first == ["Asha"] and third == ["Zoya"]
    assert first is not second, "Each call without a list needs its own new list object."


def test_fills_callers_empty_list():
    party = []
    result = invite("Meena", party)
    assert party == ["Meena"], (
        "The caller's empty list was not filled. Use `if guests is None`, not `if not guests`: "
        "an empty list is falsy, so you replaced it with a new one.")
    assert result is party, "Return the caller's own list object."


def test_fills_callers_list_twice():
    party = ["Host"]
    invite("Kiran", party)
    invite("Ravi", party)
    assert party == ["Host", "Kiran", "Ravi"], "Append to the caller's list each time."


def test_default_is_none():
    assert invite.__defaults__ == (None,), "Use None as the default for guests, not a list."
