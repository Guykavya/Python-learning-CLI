import functools

import pytest

from solution import count_calls, reset_counts


class Plain:
    def inherited(self):
        return "base"


def make_class():
    """A fresh decorated class for each test, so counts never leak between tests."""

    @count_calls
    class Account(Plain):
        rate = 0.05
        tags = ["x"]

        def __init__(self, balance=0):
            self.balance = balance

        def __repr__(self):
            return f"Account({self.balance})"

        def deposit(self, amount, *, note=""):
            """Add money."""
            self.balance += amount
            return self.balance

        def _audit(self):
            return "ok"

        def fail(self):
            raise ValueError("boom")

        @classmethod
        def empty(cls):
            """Make an empty account."""
            return cls(0)

        @staticmethod
        def fee(amount):
            return amount * 0.01

        @property
        def rich(self):
            return self.balance > 1000

        @functools.cached_property
        def report(self):
            return "report"

        class Settings:
            pass

    return Account


def test_returns_the_same_class():
    class C:
        def f(self):
            return 1

    assert count_calls(C) is C, "A class decorator that modifies the class should return the same class object."


def test_counts_start_at_zero_in_order():
    Account = make_class()
    assert Account.call_counts == {"deposit": 0, "_audit": 0, "fail": 0, "empty": 0, "fee": 0}, (
        "call_counts must list every wrapped method (plain, single-underscore, classmethod, staticmethod) with 0, "
        "and nothing else: no dunders, properties, cached_property, nested classes, data or inherited methods."
    )
    assert list(Account.call_counts) == ["deposit", "_audit", "fail", "empty", "fee"], (
        "Keep the definition order: iterate over vars(cls)."
    )


def test_plain_methods_work_and_count():
    Account = make_class()
    a = Account(5)
    assert a.deposit(10) == 15, "The wrapper must return what the method returns."
    assert a.deposit(1, note="tip") == 16, "Pass *args and **kwargs through to the method."
    Account.deposit(a, 4)
    assert Account.call_counts["deposit"] == 3, (
        "Calls through the instance and through the class (Account.deposit(a, 4)) must all count."
    )
    assert a._audit() == "ok" and Account.call_counts["_audit"] == 1, "Single-underscore methods are wrapped too."


def test_classmethod_still_receives_the_class():
    Account = make_class()

    class Savings(Account):
        pass

    acc = Account.empty()
    assert type(acc) is Account and acc.balance == 0, "Account.empty() must still receive Account as cls."
    sub = Savings.empty()
    assert type(sub) is Savings, (
        "Savings.empty() must receive Savings as cls. Wrap raw.__func__ and store classmethod(wrapper); "
        "wrapping getattr(cls, name) freezes cls to Account."
    )
    from_instance = acc.empty()
    assert type(from_instance) is Account, "Calling a classmethod on an instance passes the class, not the instance."
    assert Account.call_counts["empty"] == 3, "All three classmethod calls must be counted."
    assert isinstance(vars(Account)["empty"], classmethod), "Store a classmethod object back in the class."


def test_staticmethod_gets_no_self():
    Account = make_class()
    assert Account.fee(100) == 1.0, "A staticmethod called on the class works as before."
    assert Account(3).fee(200) == 2.0, (
        "Called on an instance, a staticmethod must NOT receive self. If you stored a plain wrapper function, "
        "the instance is passed as amount."
    )
    assert Account.call_counts["fee"] == 2, "Both staticmethod calls count."
    assert isinstance(vars(Account)["fee"], staticmethod), "Store a staticmethod object back in the class."


def test_things_left_alone():
    Account = make_class()
    raw = vars(Account)
    assert isinstance(raw["rich"], property), "Properties must stay properties (do not wrap them)."
    assert isinstance(raw["report"], functools.cached_property), "cached_property must be left alone."
    assert raw["Settings"].__name__ == "Settings" and isinstance(raw["Settings"], type), "Nested classes stay classes."
    assert raw["rate"] == 0.05 and raw["tags"] == ["x"], "Plain data must stay unchanged."
    a = Account(2000)
    assert a.rich is True and a.report == "report", "Properties keep working."
    assert repr(a) == "Account(2000)", "Dunders keep working."
    assert "__init__" not in Account.call_counts and "__repr__" not in Account.call_counts, "Dunders are not counted."
    assert "inherited" not in vars(Account), (
        "Do not copy inherited methods into the class: only wrap what is in vars(cls)."
    )
    assert a.inherited() == "base", "Inherited methods still work (they come from the base class)."


def test_raising_call_still_counts():
    Account = make_class()
    with pytest.raises(ValueError):
        Account().fail()
    assert Account.call_counts["fail"] == 1, "Count before calling the method, so a call that raises is counted too."


def test_metadata_kept():
    Account = make_class()
    assert Account.deposit.__name__ == "deposit", "Use functools.wraps so the wrapper keeps the method's __name__."
    assert Account.deposit.__doc__ == "Add money.", "functools.wraps also copies the docstring."
    assert Account.empty.__doc__ == "Make an empty account.", "The classmethod's inner function must keep its docstring."


def test_counts_are_per_class():
    A = make_class()
    B = make_class()
    A().deposit(1)
    assert A.call_counts["deposit"] == 1 and B.call_counts["deposit"] == 0, (
        "Each decorated class needs its own counts dict (create it inside count_calls, not at module level)."
    )


def test_reset_counts():
    Account = make_class()
    Account().deposit(1)
    Account.fee(1)
    reset_counts(Account)
    assert Account.call_counts == {"deposit": 0, "_audit": 0, "fail": 0, "empty": 0, "fee": 0}, (
        "reset_counts sets every count to 0 and keeps all the keys."
    )
    Account().deposit(1)
    assert Account.call_counts["deposit"] == 1, (
        "After reset, the wrappers must still update cls.call_counts: change the values in the same dict, "
        "do not replace it with a new dict the wrappers do not know about."
    )
