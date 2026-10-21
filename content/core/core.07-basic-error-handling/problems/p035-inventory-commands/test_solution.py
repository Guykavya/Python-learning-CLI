import ast
from pathlib import Path

from solution import process

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


def run(commands, stock=None):
    """Call process; turn an escaping exception into a clear failure."""
    stock = {} if stock is None else stock
    try:
        return process(commands, stock)
    except (ValueError, KeyError) as e:
        raise AssertionError(
            f"process let {type(e).__name__}({e}) escape. Bad commands must become 'error: ...' replies; "
            "catch ValueError and KeyError in process, around each command.") from e


def test_unknown_verb():
    got = run(["sell apple 1", "Dance"], {"apple": 1})
    assert got == ["error: unknown command 'sell'; use add, remove, show or list",
                   "error: unknown command 'dance'; use add, remove, show or list"], (
        f"Got {got}. Check `verb in HANDLERS` first: HANDLERS[verb] raises KeyError for an unknown verb, "
        "which would be reported as a missing item.")


def test_example():
    stock = {"apple": 5}
    got = run(["add Banana 12", "remove apple 2", "remove apple 9", "show kiwi",
               "add pear lots", "sell apple 1", "list"], stock)
    assert got == ["banana: 12", "apple: 3", "error: only 3 apple in stock, cannot remove 9",
                   "error: no item 'kiwi' in stock",
                   "error: quantity must be a positive whole number, got 'lots'",
                   "error: unknown command 'sell'; use add, remove, show or list",
                   "apple: 3, banana: 12"], f"Got {got}"
    assert stock == {"apple": 3, "banana": 12}, f"Got stock {stock}. Change the caller's dict in place."


def test_one_reply_per_command():
    assert len(run(["", "list", "nonsense", "add a 1"])) == 4, "Every command, good or bad, gets exactly one reply."


def test_empty_and_list():
    assert run(["   "]) == ["error: empty command"]
    assert run(["list"]) == ["empty"], "An empty stock lists as 'empty'."
    assert run(["LIST"], {"b": 1, "a": 2}) == ["a: 2, b: 1"], "Verbs are case-insensitive; list sorted by name."


def test_usage_messages():
    got = run(["add apple", "remove apple 1 2", "show", "list all"], {"apple": 1})
    assert got == ["error: usage: add <item> <qty>", "error: usage: remove <item> <qty>",
                   "error: usage: show <item>", "error: usage: list"], (
        f"Got {got}. Check the number of words in each handler and raise ValueError('usage: ...').")


def test_quantity_rules():
    got = run(["add x 0", "add x -3", "add x 2.5", "add x 3"])
    assert got == ["error: quantity must be a positive whole number, got '0'",
                   "error: quantity must be a positive whole number, got '-3'",
                   "error: quantity must be a positive whole number, got '2.5'",
                   "x: 3"], f"Got {got}."


def test_missing_item():
    stock = {"apple": 1}
    assert run(["remove Kiwi 1", "show KIWI"], stock) == ["error: no item 'kiwi' in stock"] * 2, (
        "Look the lower-cased item up; report the missing one with !r.")
    assert stock == {"apple": 1}, "A failed command must not create the item."


def test_remove_too_many_keeps_stock():
    stock = {"apple": 3}
    assert run(["remove apple 4", "remove apple 3"], stock) == [
        "error: only 3 apple in stock, cannot remove 4", "apple: 0"]
    assert stock == {"apple": 0}


def test_bugs_propagate():
    expect_raise(TypeError, process, ["add apple 2"], {"apple": "5"},
                 why="'5' + 2 is a bug in the data, not a bad command. Catch only ValueError and KeyError.")


def test_no_broad_except():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "No bare `except:`."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), (
                "Translate only ValueError and KeyError at the boundary.")
