import sqlite3

import pytest

from solution import accounts_with_prefix, balance, open_bank, transfer

START = {"asha": 100, "ravi": 50, "zoya": 10}


@pytest.fixture
def bank(tmp_path):
    path = tmp_path / "bank.db"
    conn = open_bank(str(path), START)
    other = sqlite3.connect(str(path))       # a second connection, like another program
    try:
        yield conn, other
    finally:
        conn.close()
        other.close()


def seen_by_other(other, name):
    return other.execute("SELECT balance FROM accounts WHERE name = ?", (name,)).fetchone()[0]


def test_open_and_balance(bank):
    conn, other = bank
    assert isinstance(conn, sqlite3.Connection), "open_bank must return the sqlite3 connection."
    assert [balance(conn, n) for n in ("asha", "ravi", "zoya")] == [100, 50, 10], "Insert every account of the dict with executemany."
    assert seen_by_other(other, "asha") == 100, "The accounts must be committed in open_bank: another connection cannot see them yet."


def test_balance_unknown(bank):
    conn, _ = bank
    with pytest.raises(KeyError):
        balance(conn, "nobody")


def test_transfer_success_is_committed(bank):
    conn, other = bank
    transfer(conn, "asha", "ravi", 30)
    assert (balance(conn, "asha"), balance(conn, "ravi")) == (70, 80), "30 moves from asha to ravi."
    assert (seen_by_other(other, "asha"), seen_by_other(other, "ravi")) == (70, 80), (
        "Another connection must see the transfer: commit it (leave a `with conn:` block normally)."
    )
    assert not conn.in_transaction, "After transfer returns, no transaction may be left open."


def test_transfer_whole_balance(bank):
    conn, _ = bank
    transfer(conn, "zoya", "asha", 10)
    assert balance(conn, "zoya") == 0, "Sending the exact balance is allowed: 0 satisfies CHECK (balance >= 0)."


def test_insufficient_funds_rolls_back(bank):
    conn, other = bank
    with pytest.raises(ValueError):
        transfer(conn, "zoya", "asha", 500)
    assert (balance(conn, "zoya"), balance(conn, "asha")) == (10, 100), "A refused transfer changes nothing."
    assert not conn.in_transaction, "The failed transaction must be rolled back, not left open."
    transfer(conn, "zoya", "asha", 5)
    assert seen_by_other(other, "zoya") == 5, "After a refused transfer the next one must still work and be committed."


def test_unknown_destination_rolls_back_debit(bank):
    conn, other = bank
    with pytest.raises(KeyError):
        transfer(conn, "asha", "rahul", 30)
    assert balance(conn, "asha") == 100, (
        "The debit of asha must be undone when the destination does not exist: both updates belong to ONE transaction "
        "and an exception inside `with conn:` rolls it back."
    )
    assert not conn.in_transaction, "Nothing may stay pending after the failed transfer."
    conn.commit()
    assert seen_by_other(other, "asha") == 100, "Even a later commit must not save half a transfer."


def test_unknown_source(bank):
    conn, _ = bank
    with pytest.raises(KeyError):
        transfer(conn, "rahul", "asha", 1)
    assert balance(conn, "asha") == 100, "Nobody can receive money from an account that does not exist."


@pytest.mark.parametrize("amount", [0, -5, 2.5, "10"])
def test_bad_amounts(bank, amount):
    conn, _ = bank
    with pytest.raises(ValueError):
        transfer(conn, "asha", "ravi", amount)
    assert balance(conn, "asha") == 100 and balance(conn, "ravi") == 50, "A bad amount must be refused before any update."


def test_same_account(bank):
    conn, _ = bank
    with pytest.raises(ValueError):
        transfer(conn, "asha", "asha", 10)


def test_money_is_conserved(bank):
    conn, _ = bank
    for src, dst, amt in [("asha", "ravi", 40), ("ravi", "zoya", 70), ("zoya", "asha", 999), ("zoya", "nobody", 1), ("zoya", "asha", 80)]:
        try:
            transfer(conn, src, dst, amt)
        except (ValueError, KeyError):
            pass
    total = sum(balance(conn, n) for n in START)
    assert total == 160, "Whatever succeeds or fails, the total money must stay 160: no transfer may be half-applied."
    assert (balance(conn, "asha"), balance(conn, "ravi"), balance(conn, "zoya")) == (140, 20, 0), "Check the order of the five transfers."


def test_prefix_search(bank):
    conn, _ = bank
    assert accounts_with_prefix(conn, "a") == ["asha"], "Names starting with 'a'."
    assert accounts_with_prefix(conn, "") == ["asha", "ravi", "zoya"], "The empty prefix matches every name, sorted."
    assert accounts_with_prefix(conn, "A") == [], "The match is case-sensitive."


def test_prefix_injection(bank):
    conn, _ = bank
    assert accounts_with_prefix(conn, "nobody' OR 1=1 --") == [], (
        "The injection text must be treated as a plain prefix: pass it as a ? parameter, never inside the SQL string."
    )
    assert accounts_with_prefix(conn, "'") == [], "A lone quote must not break the query."


def test_prefix_wildcards_are_literal(tmp_path):
    conn = open_bank(str(tmp_path / "w.db"), {"a_b": 1, "abc": 2, "a%x": 3, "o'neil": 4})
    try:
        assert accounts_with_prefix(conn, "a_") == ["a_b"], "'_' is a LIKE wildcard; here it must match only a real underscore."
        assert accounts_with_prefix(conn, "a%") == ["a%x"], "'%' must match only a real percent sign."
        assert accounts_with_prefix(conn, "o'") == ["o'neil"], "A quote in the prefix is just a character."
    finally:
        conn.close()
