import ast
from pathlib import Path

from solution import load_score

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


def test_found():
    log = []
    assert load_score({"asha": 82}, "asha", log) == 82
    assert log == [], "Nothing went wrong, so nothing should be logged."


def test_missing_is_logged_and_reraised():
    log = []
    error = expect_raise(KeyError, load_score, {"asha": 82}, "ravi", log,
                         why="After logging, re-raise with a bare `raise`; do not return.")
    assert log == ["missing score: ravi"], f"Got log {log}. Append 'missing score: <name>' before re-raising."
    assert error.args == ("ravi",), (
        "The caller must see the ORIGINAL KeyError('ravi'). Use a bare `raise`, not a new exception.")


def test_log_accumulates():
    log = ["earlier"]
    for name in ["x", "y"]:
        expect_raise(KeyError, load_score, {}, name, log, why="Re-raise after logging.")
    assert log == ["earlier", "missing score: x", "missing score: y"], "Append to the caller's list; do not replace it."


def test_other_errors_not_logged():
    log = []
    expect_raise(TypeError, load_score, {"asha": 82}, ["asha"], log,
                 why="A list name is unhashable: TypeError must pass through. Catch KeyError only.")
    assert log == [], "Only a KeyError is logged. A TypeError (unhashable key) must pass straight through."


def test_uses_bare_raise():
    raises = [n for n in ast.walk(TREE) if isinstance(n, ast.Raise)]
    assert any(r.exc is None for r in raises), "Re-raise with a bare `raise` inside the except block."
    for h in ast.walk(TREE):
        if isinstance(h, ast.ExceptHandler):
            assert h.type is not None and ast.unparse(h.type) == "KeyError", "Catch KeyError only."
