import pytest

from solution import (AccountFrozen, AccountNotFound, Bank, BankError, InsufficientFunds,
                      TransferError, Account)


def make_bank():
    bank = Bank()
    bank.open("A", "Asha", 100)
    bank.open("B", "Ben")
    return bank


def balances(bank):
    return bank.get("A").balance, bank.get("B").balance


# ---------------------------------------------------------------- exceptions

def test_hierarchy():
    for cls in (AccountNotFound, InsufficientFunds, AccountFrozen, TransferError):
        assert issubclass(cls, BankError), f"{cls.__name__} must inherit from BankError, so callers can catch all bank errors at once."
    assert issubclass(BankError, Exception), "BankError inherits from Exception."


def test_exception_attributes_and_messages():
    e = InsufficientFunds("A", 50, 80)
    assert (e.account_id, e.balance, e.amount) == ("A", 50, 80), "InsufficientFunds stores account_id, balance, amount."
    assert str(e) == "account 'A' has 50, needs 80", f"Message format from problem.md. Got {str(e)!r}."
    assert str(AccountNotFound("X")) == "no account 'X'" and AccountNotFound("X").account_id == "X", "AccountNotFound('X'): 'no account 'X''."
    assert str(AccountFrozen("B")) == "account 'B' is frozen", "AccountFrozen message."
    t = TransferError("A", "B", 80)
    assert (t.source, t.target, t.amount) == ("A", "B", 80), "TransferError stores source, target, amount."
    assert str(t) == "transfer of 80 from 'A' to 'B' failed", f"TransferError message. Got {str(t)!r}."


# ---------------------------------------------------------------- Account

def test_account_basics():
    acc = Account("A", "Asha", 100)
    acc.deposit(50)
    acc.withdraw(30)
    assert acc.balance == 120, "100 + 50 - 30 = 120."
    assert (acc.account_id, acc.owner, acc.frozen) == ("A", "Asha", False), "Store account_id and owner; frozen starts False."


def test_balance_is_read_only():
    acc = Account("A", "Asha", 100)
    with pytest.raises(AttributeError):
        acc.balance = 10 ** 6
    assert acc.balance == 100, "balance is a read-only property: no setter."


@pytest.mark.parametrize("bad", [-1, 1.5, "10", True])
def test_bad_opening_balance(bad):
    with pytest.raises(ValueError, match="balance must be an int >= 0"):
        Account("A", "Asha", bad)


@pytest.mark.parametrize("bad", [0, -5, 2.5, "3", True])
def test_bad_amounts(bad):
    acc = Account("A", "Asha", 100)
    with pytest.raises(ValueError, match="amount must be a positive int"):
        acc.deposit(bad)
    with pytest.raises(ValueError, match="amount must be a positive int"):
        acc.withdraw(bad)
    assert acc.balance == 100, "A failed call changes nothing."


def test_insufficient_funds():
    acc = Account("A", "Asha", 50)
    with pytest.raises(InsufficientFunds) as info:
        acc.withdraw(80)
    assert (info.value.balance, info.value.amount) == (50, 80), "Raise InsufficientFunds(account_id, balance, amount)."
    assert acc.balance == 50, "Nothing changes after a failed withdrawal."
    acc.withdraw(50)
    assert acc.balance == 0, "Withdrawing exactly the balance is fine."


def test_frozen_account():
    acc = Account("A", "Asha", 50)
    acc.freeze()
    assert acc.frozen is True, "freeze() sets frozen to True."
    with pytest.raises(AccountFrozen):
        acc.deposit(10)
    with pytest.raises(AccountFrozen):
        acc.withdraw(10)
    assert acc.balance == 50, "A frozen account keeps its balance."


def test_check_order_amount_first():
    acc = Account("A", "Asha", 50)
    acc.freeze()
    with pytest.raises(ValueError):
        acc.withdraw(-1)  # bad amount is checked before frozen
    acc2 = Account("B", "Ben", 10)
    acc2.freeze()
    with pytest.raises(AccountFrozen):
        acc2.withdraw(1000)  # frozen is checked before funds


# ---------------------------------------------------------------- Bank

def test_open_and_get():
    bank = Bank()
    acc = bank.open("A", "Asha", 100)
    assert bank.get("A") is acc, "open returns the new Account and get returns that same object."
    with pytest.raises(ValueError, match="account 'A' already exists"):
        bank.open("A", "Someone")


def test_get_missing_account():
    with pytest.raises(AccountNotFound, match="no account 'Z'") as info:
        Bank().get("Z")
    assert info.value.__cause__ is None and info.value.__suppress_context__, (
        "Use raise AccountNotFound(account_id) from None: the KeyError adds nothing to the traceback."
    )


def test_successful_transfer():
    bank = make_bank()
    assert bank.transfer("A", "B", 30) is None, "transfer returns None on success."
    assert balances(bank) == (70, 30), "30 moves from A to B."
    assert bank.statement() == ["ok 30 A->B"], "A successful transfer adds 'ok 30 A->B'."


def check_failed_transfer(bank, source, target, amount, cause_type, before):
    with pytest.raises(TransferError) as info:
        bank.transfer(source, target, amount)
    err = info.value
    assert (err.source, err.target, err.amount) == (source, target, amount), "TransferError(source_id, target_id, amount)."
    assert isinstance(err.__cause__, cause_type), (
        f"__cause__ should be a {cause_type.__name__}, got {type(err.__cause__).__name__}. "
        "Use raise TransferError(...) from err."
    )
    assert balances(bank) == before, f"After a failed transfer the balances must be unchanged: expected {before}, got {balances(bank)}."
    return err


def test_insufficient_funds_transfer():
    bank = make_bank()
    check_failed_transfer(bank, "A", "B", 500, InsufficientFunds, (100, 0))


def test_unknown_accounts():
    bank = make_bank()
    err = check_failed_transfer(bank, "A", "Z", 10, AccountNotFound, (100, 0))
    assert err.__cause__.account_id == "Z", "The cause names the missing account."
    check_failed_transfer(bank, "Q", "A", 10, AccountNotFound, (100, 0))


def test_bad_amount_transfer():
    bank = make_bank()
    check_failed_transfer(bank, "A", "B", 0, ValueError, (100, 0))
    check_failed_transfer(bank, "A", "B", 1.5, ValueError, (100, 0))


def test_same_account():
    bank = make_bank()
    err = check_failed_transfer(bank, "A", "A", 10, ValueError, (100, 0))
    assert str(err.__cause__) == "cannot transfer to the same account", "Same account: the cause is ValueError('cannot transfer to the same account')."


def test_rollback_when_deposit_fails():
    bank = make_bank()
    bank.get("B").freeze()
    err = check_failed_transfer(bank, "A", "B", 20, AccountFrozen, (100, 0))
    assert err.__cause__.account_id == "B", (
        "The deposit into frozen B failed. The money taken from A must be put back (undo), "
        "and the cause is AccountFrozen('B')."
    )


def test_frozen_source():
    bank = make_bank()
    bank.get("A").freeze()
    check_failed_transfer(bank, "A", "B", 20, AccountFrozen, (100, 0))


def test_statement_records_everything():
    bank = make_bank()
    bank.transfer("A", "B", 30)
    bank.get("B").freeze()
    for args in (("A", "B", 20), ("A", "B", 500), ("A", "Z", 5)):
        with pytest.raises(TransferError):
            bank.transfer(*args)
    assert bank.statement() == [
        "ok 30 A->B",
        "failed 20 A->B: account 'B' is frozen",
        "failed 500 A->B: account 'A' has 70, needs 500",
        "failed 5 A->Z: no account 'Z'",
    ], f"Got {bank.statement()}. One line per transfer call; failures show str() of the cause."


def test_statement_is_a_copy():
    bank = make_bank()
    bank.transfer("A", "B", 1)
    bank.statement().clear()
    assert bank.statement() == ["ok 1 A->B"], "statement() returns a NEW list each time."


def test_catch_as_bank_error():
    bank = make_bank()
    try:
        bank.transfer("A", "B", 10 ** 9)
    except BankError:
        pass
    else:
        pytest.fail("A failed transfer must raise (a TransferError is a BankError).")
