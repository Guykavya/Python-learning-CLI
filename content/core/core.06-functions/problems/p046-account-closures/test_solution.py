from solution import make_account
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_example():
    acct = make_account(100)
    assert acct["deposit"](50) == 150
    assert acct["withdraw"](30) == 120
    assert acct["withdraw"](500) is None, "Withdrawing more than the balance returns None."
    assert acct["balance"]() == 120, (
        "balance() must return the CURRENT balance. Did you store a value instead of the function?")


def test_refusals_change_nothing():
    acct = make_account(10)
    assert acct["deposit"](0) is None and acct["deposit"](-5) is None
    assert acct["withdraw"](-1) is None and acct["withdraw"](11) is None
    assert acct["balance"]() == 10


def test_withdraw_everything():
    acct = make_account(40)
    assert acct["withdraw"](40) == 0


def test_independent_accounts():
    a = make_account(100)
    b = make_account()
    a["deposit"](1)
    assert b["balance"]() == 0, "Accounts must not share a balance."
    b["deposit"](5)
    assert a["balance"]() == 101 and b["balance"]() == 5


def test_values_are_functions():
    acct = make_account()
    assert set(acct) == {"deposit", "withdraw", "balance"}
    assert all(callable(f) for f in acct.values())


def test_no_globals():
    assert not any(isinstance(n, ast.Global) for n in ast.walk(TREE)), "Use closures and nonlocal, not global."
