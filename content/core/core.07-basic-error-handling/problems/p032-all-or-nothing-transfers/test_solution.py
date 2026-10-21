from solution import apply_transfers


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


def test_all_succeed():
    accounts = {"asha": 100, "ravi": 50}
    same = accounts
    assert apply_transfers(accounts, [("asha", "ravi", 30), ("ravi", "asha", 70)]) == 2
    assert accounts == {"asha": 140, "ravi": 10}, (
        f"Got {accounts}. Apply in order: ravi can send 70 only after receiving 30.")
    assert accounts is same, "Update the caller's dict itself."


def test_no_transfers():
    accounts = {"asha": 1}
    assert apply_transfers(accounts, []) == 0 and accounts == {"asha": 1}


def test_unknown_receiver_rolls_back():
    accounts = {"asha": 140, "ravi": 10}
    err = expect_raise(KeyError, apply_transfers, accounts, [("asha", "ravi", 40), ("ravi", "zoya", 5)],
                       why="An unknown account raises KeyError.")
    assert err.args == ("zoya",), f"The KeyError's argument should be the missing name, got {err.args}."
    assert accounts == {"asha": 140, "ravi": 10}, (
        f"Got {accounts}. The first transfer had already been applied: on failure the balances must be "
        "exactly as before the call (and 'zoya' must not be created).")


def test_unknown_sender():
    accounts = {"asha": 10}
    err = expect_raise(KeyError, apply_transfers, accounts, [("meena", "asha", 5)])
    assert err.args == ("meena",)
    assert accounts == {"asha": 10}


def test_insufficient_funds_rolls_back():
    accounts = {"a": 50, "b": 0, "c": 0}
    transfers = [("a", "b", 20), ("b", "c", 20), ("a", "c", 40)]
    expect_raise(ValueError, apply_transfers, accounts, transfers, match="transfer 3: a has 30, cannot send 40",
                 why="Check the sender's balance at that point in the batch.")
    assert accounts == {"a": 50, "b": 0, "c": 0}, f"Got {accounts}. Nothing may change when a transfer fails."


def test_amount_must_be_positive():
    accounts = {"a": 50, "b": 0}
    expect_raise(ValueError, apply_transfers, accounts, [("a", "b", 10), ("b", "a", 0)],
                 match="transfer 2: amount must be positive, got 0")
    expect_raise(ValueError, apply_transfers, accounts, [("a", "b", -5)], match="got -5",
                 why="A negative amount would move money the wrong way.")
    assert accounts == {"a": 50, "b": 0}


def test_exact_balance_allowed():
    accounts = {"a": 25, "b": 0}
    assert apply_transfers(accounts, [("a", "b", 25)]) == 1 and accounts == {"a": 0, "b": 25}, (
        "Sending exactly the whole balance is allowed.")


def test_repeated_calls_independent():
    accounts = {"a": 10, "b": 0}
    apply_transfers(accounts, [("a", "b", 4)])
    expect_raise(ValueError, apply_transfers, accounts, [("a", "b", 7)], match="a has 6, cannot send 7")
    assert accounts == {"a": 6, "b": 4}
