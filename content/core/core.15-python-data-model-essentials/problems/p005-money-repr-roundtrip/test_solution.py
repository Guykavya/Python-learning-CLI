from solution import Money


def test_repr_text():
    assert repr(Money(1250, "USD")) == "Money(1250, 'USD')", "repr should mirror the constructor call: Money(1250, 'USD')."


def test_roundtrip():
    m = Money(1250, "USD")
    assert eval(repr(m), {"Money": Money}) == m, "eval(repr(m)) must rebuild an equal Money. Is your repr valid Python?"


def test_roundtrip_negative_and_zero():
    for m in (Money(0, "EUR"), Money(-5, "EUR"), Money(99999, "INR")):
        assert eval(repr(m), {"Money": Money}) == m, f"repr of {m!s} does not rebuild the same object."


def test_str_basic():
    assert str(Money(1250, "USD")) == "12.50 USD", "str should show two decimals and the currency: '12.50 USD'."


def test_str_small_cents_padded():
    assert str(Money(5, "USD")) == "0.05 USD", "5 cents is '0.05': pad the cents to two digits with :02d."
    assert str(Money(100, "USD")) == "1.00 USD", "100 cents is '1.00 USD'."


def test_str_negative():
    assert str(Money(-5, "EUR")) == "-0.05 EUR", "Negative amounts start with '-': take abs() before divmod, then add the sign."
    assert str(Money(-1234, "EUR")) == "-12.34 EUR", "-1234 cents is '-12.34 EUR'."


def test_str_zero():
    assert str(Money(0, "USD")) == "0.00 USD", "Zero is '0.00 USD', with no minus sign."


def test_list_shows_repr():
    assert str([Money(1, "USD")]) == "[Money(1, 'USD')]", "Inside a list Python uses repr."
