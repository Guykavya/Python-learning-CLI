import pytest

from solution import CurrencyMismatchError, Money


def test_add_and_sub():
    assert Money(500, "USD") + Money(250, "USD") == Money(750, "USD"), "Same currency: add the cents."
    assert Money(500, "USD") - Money(250, "USD") == Money(250, "USD"), "Same currency: subtract the cents."
    assert Money(100, "USD") - Money(250, "USD") == Money(-150, "USD"), "Negative results are allowed."


def test_new_object_and_operands_unchanged():
    a, b = Money(1, "USD"), Money(2, "USD")
    r = a + b
    assert r is not a and (a.cents, b.cents) == (1, 2), "+ must return a new Money and not change the operands."


def test_mismatch_add():
    with pytest.raises(CurrencyMismatchError) as e:
        Money(100, "USD") + Money(100, "EUR")
    msg = str(e.value)
    assert "USD" in msg and "EUR" in msg, "The error message should name both currencies, e.g. 'cannot mix USD and EUR'."


def test_mismatch_sub_and_type():
    with pytest.raises(CurrencyMismatchError):
        Money(100, "USD") - Money(100, "EUR")
    assert issubclass(CurrencyMismatchError, ValueError), "CurrencyMismatchError must stay a ValueError."


def test_other_types_are_typeerror_not_mismatch():
    with pytest.raises(TypeError) as e:
        Money(100, "USD") + 5
    assert not isinstance(e.value, CurrencyMismatchError), "A non-Money operand is a type problem: return NotImplemented, do not raise CurrencyMismatchError."
    with pytest.raises(TypeError):
        Money(100, "USD") - "x"


def test_multiply_by_int_both_sides():
    assert Money(500, "USD") * 3 == Money(1500, "USD"), "Money * int multiplies the cents."
    assert 3 * Money(500, "USD") == Money(1500, "USD"), "int * Money needs __rmul__."
    assert Money(500, "USD") * 0 == Money(0, "USD"), "Times 0 is zero cents."


def test_multiply_rejects_float_and_money():
    with pytest.raises(TypeError):
        Money(100, "USD") * 0.5
    with pytest.raises(TypeError):
        Money(100, "USD") * Money(1, "USD")
    with pytest.raises(TypeError):
        1.5 * Money(100, "USD")


def test_neg():
    n = -Money(500, "USD")
    assert n == Money(-500, "USD"), "-m negates the cents and keeps the currency."


def test_eq_across_currencies_is_false_not_error():
    assert not (Money(100, "USD") == Money(100, "EUR")), "Same cents, different currency: just not equal (no exception)."
