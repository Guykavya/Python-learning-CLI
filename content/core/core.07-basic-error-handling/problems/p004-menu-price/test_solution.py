import ast
from pathlib import Path

from solution import price_message

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())
MENU = {"tea": 15, "coffee": 25, "samosa": 20}

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


def test_item_on_menu():
    assert price_message(MENU, "tea") == "tea costs Rs 15", "Format: '<item> costs Rs <price>'."
    assert price_message(MENU, "samosa") == "samosa costs Rs 20"


def test_missing_item_lists_sorted_menu():
    got = price_message(MENU, "cake")
    assert got == "Sorry, 'cake' is not on the menu. Choose one of: coffee, samosa, tea.", (
        f"Got {got!r}. Show the item with repr (!r), then the menu items sorted and joined with ', ', "
        "ending with a full stop.")


def test_menu_not_changed():
    menu = dict(MENU)
    price_message(menu, "cake")
    assert menu == MENU, "Do not add the missing item to the menu; only report it."


def test_empty_menu():
    got = price_message({}, "tea")
    assert got == "Sorry, 'tea' is not on the menu. The menu is empty today.", (
        f"Got {got!r}. With an empty menu there is nothing to list: use the 'empty today' sentence.")


def test_unhashable_item_is_a_bug():
    expect_raise(TypeError, price_message, MENU, ["tea"],
                 why="A list cannot be a dict key: that is the caller's bug. Catch KeyError only.")


def test_catches_key_error_only():
    handlers = [n for n in ast.walk(TREE) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "Use try/except KeyError for the lookup (EAFP), as the problem asks."
    for h in handlers:
        assert h.type is not None and ast.unparse(h.type) == "KeyError", (
            "Catch exactly KeyError. A wider handler would also hide the TypeError bug.")
