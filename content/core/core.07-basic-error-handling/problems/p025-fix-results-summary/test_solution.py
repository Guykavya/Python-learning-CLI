import ast
from pathlib import Path

from solution import parse_result, summarise

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


def test_average_of_good_lines():
    got = summarise(["Asha,82", "Ravi,78"])
    assert got == (80.0, []), (
        f"Got {got}. The average is always None: something inside the average `try` raises every time "
        "and the broad handler hides it. Narrow that handler to ZeroDivisionError and read the traceback.")


def test_no_valid_lines():
    assert summarise([]) == (None, []), "No marks at all: the average is None (handle ZeroDivisionError)."


def test_parse_good_line():
    assert parse_result(" Asha , 82") == ("Asha", 82), "Strip the name; int() ignores spaces around marks."


def test_wrong_field_count_message():
    expect_raise(ValueError, parse_result, "Meena,75,80", match="expected 'name,marks', got 'Meena,75,80'",
                 why="Three fields is not a marks problem. Check len(parts) before converting, "
                     "instead of letting the unpacking error be caught as 'not a whole number'.")
    expect_raise(ValueError, parse_result, "Kiran", match="expected 'name,marks', got 'Kiran'")


def test_not_a_number_message():
    expect_raise(ValueError, parse_result, "Ravi, eighty", match="marks must be a whole number, got 'eighty'",
                 why="Show the stripped marks text with !r.")


def test_range_message():
    expect_raise(ValueError, parse_result, "Zoya,120", match="marks must be from 0 to 100, got 120",
                 why="The bare except replaced your range message with the 'whole number' one.")
    expect_raise(ValueError, parse_result, "Zoya,-1", match="got -1")
    assert parse_result("A,0") == ("A", 0) and parse_result("B,100") == ("B", 100), "0 and 100 are allowed."


def test_bug_is_not_disguised():
    try:
        parse_result(None)
    except ValueError:
        raise AssertionError(
            "parse_result(None) is a programming bug, but it was turned into a ValueError about marks. "
            "That is what the bare except does: remove it.") from None
    except Exception:
        pass


def test_errors_are_collected():
    got = summarise(["Asha,82", "Meena,75,80", "Ravi,eighty"])
    assert got == (82.0, ["line 2: expected 'name,marks', got 'Meena,75,80'",
                          "line 3: marks must be a whole number, got 'eighty'"]), (
        f"Got {got}. `except Exception: pass` threw the errors away. Catch ValueError as e and "
        "append f'line {number}: {e}'.")


def test_no_broad_handlers():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "Remove the bare `except:`; it hides bugs."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), (
                "Replace `except Exception` with the specific exception you expect.")
