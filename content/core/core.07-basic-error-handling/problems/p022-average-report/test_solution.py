import ast
from pathlib import Path

from solution import average_report

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


def test_example():
    got = average_report({"Ravi": [70, 81], "Asha": [80, 77, 78.5], "Zoya": []})
    assert got == ["Asha: 78.5", "Ravi: 75.5", "Zoya: no marks yet"], f"Got {got}."


def test_one_decimal_always():
    assert average_report({"Kiran": [90]}) == ["Kiran: 90.0"], "Format with :.1f, so 90 shows as 90.0."


def test_empty_dict():
    assert average_report({}) == [], "No students: return an empty list."


def test_only_empty_lists():
    assert average_report({"B": [], "A": []}) == ["A: no marks yet", "B: no marks yet"], "Sort by name."


def test_bad_data_propagates():
    expect_raise(TypeError, average_report, {"Asha": [80, "77"]},
                 why="A string in the marks is bad data: catch ZeroDivisionError only.")


def test_input_unchanged():
    data = {"Ravi": [70, 81], "Asha": []}
    average_report(data)
    assert data == {"Ravi": [70, 81], "Asha": []}, "Do not change the caller's dict."


def test_try_is_narrow():
    tries = [n for n in ast.walk(TREE) if isinstance(n, ast.Try)]
    assert tries, "Use try/except ZeroDivisionError for the empty list."
    for t in tries:
        assert len(t.body) == 1, (
            "Keep the try block to ONE statement, the average computation. Build the line in `else`.")
        for h in t.handlers:
            assert h.type is not None and ast.unparse(h.type) == "ZeroDivisionError", "Catch ZeroDivisionError only."
