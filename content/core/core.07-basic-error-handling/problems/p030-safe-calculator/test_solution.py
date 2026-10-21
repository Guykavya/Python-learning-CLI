import ast
from pathlib import Path

from solution import calculate

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())
SHAPE = "Error: write it as <number> <operator> <number>, for example 12 / 4"


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


def calc(expression):
    """Call calculate and turn any escaping exception into a clear failure."""
    try:
        return calculate(expression)
    except Exception as e:
        raise AssertionError(
            f"calculate({expression!r}) raised {type(e).__name__}: {e}. It must return a message "
            "for every string.") from e


def test_operations():
    cases = {"12 / 4": "3.0", "2 ** 10": "1024.0", "7 // 2": "3.0", "7 % 3": "1.0",
             "1.5 + 2": "3.5", "3 - 10": "-7.0", "-2 * 4": "-8.0"}
    for expr, want in cases.items():
        got = calc(expr)
        assert got == want, f"calculate({expr!r}) gave {got!r}, expected {want!r}. Return str() of the float result."


def test_extra_spaces_are_fine():
    assert calc("  12   /  4 ") == "3.0", "Use split() with no argument: it handles any amount of whitespace."


def test_shape():
    for expr in ["12 /", "", "   ", "1 + 2 + 3", "12/4"]:
        assert calc(expr) == SHAPE, f"{expr!r} does not have exactly three parts: return the shape message."


def test_not_a_number():
    assert calc("ten / 2") == "Error: 'ten' is not a number"
    assert calc("10 / two") == "Error: 'two' is not a number"
    assert calc("x * y") == "Error: 'x' is not a number", "Report the FIRST bad number."
    assert calc("nan + 1") == "Error: 'nan' is not a number", "float('nan') works, but nan is not finite: reject it."
    assert calc("1 * inf") == "Error: 'inf' is not a number"


def test_unknown_operator():
    assert calc("12 x 4") == "Error: unknown operator 'x'; use one of + - * / // % **"
    assert calc("2 ^ 3") == "Error: unknown operator '^'; use one of + - * / // % **"


def test_numbers_checked_before_operator():
    assert calc("a x 4") == "Error: 'a' is not a number", "Check both numbers before the operator."


def test_zero_division():
    for expr in ["5 / 0", "5 // 0.0", "5 % 0", "0 / 0"]:
        assert calc(expr) == "Error: cannot divide by zero", f"{expr!r}: catch ZeroDivisionError."


def test_too_large():
    assert calc("10 ** 400") == "Error: the result is too large", "10.0 ** 400 raises OverflowError: catch it."
    assert calc("1e308 * 10") == "Error: the result is too large", (
        "1e308 * 10 raises nothing: the result is inf. Check math.isfinite(result) after computing.")
    assert calc("-1e308 - 1e308") == "Error: the result is too large"


def test_complex_result():
    assert calc("-8 ** 0.5") == "Error: the result is not a real number", (
        "A negative float to a fractional power is a complex number in Python. Check isinstance(result, complex).")


def test_never_raises_on_odd_strings():
    for expr in ["1 / 1e-320", "0 ** -1", "1e400 + 1", "-0 * 5", "٣ + 1", "1_0 + 1", "+ + +"]:
        calc(expr)


def test_type_error_for_non_string():
    expect_raise(TypeError, calculate, 42, match="expression must be text (str), got int",
                 why="A non-string is a programming bug: raise TypeError, do not return a message.")


def test_no_broad_except():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "No bare `except:`. Catch the specific exceptions each step can raise."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), (
                "Do not catch Exception to 'never crash'. Name ValueError, ZeroDivisionError, OverflowError.")
