import pytest

from solution import CurrencyMismatchError, Money


def test_basic_and_read_only():
    m = Money(1250, "INR")
    assert (m.minor, m.currency) == (1250, "INR"), "Store minor and currency."
    with pytest.raises(AttributeError):
        m.minor = 5
    with pytest.raises(AttributeError):
        m.currency = "USD"
    assert Money(-305, "USD").minor == -305, "Negative amounts are allowed."


def test_bad_construction():
    for bad in (12.5, "1250", None):
        with pytest.raises(TypeError):
            Money(bad, "INR")
    for code in ("inr", "IN", "INRS", "I1R", 356, ""):
        with pytest.raises(ValueError):
            Money(100, code)


def test_from_string():
    cases = {"12.50 INR": 1250, "12 INR": 1200, "12.5 INR": 1250, "-3.05 USD": -305, "0.07 EUR": 7, "0 INR": 0}
    for text, minor in cases.items():
        m = Money.from_string(text)
        assert m.minor == minor, f"from_string({text!r}).minor should be {minor}."
    assert Money.from_string("-3.05 USD").currency == "USD", "The code after the space is the currency."


def test_from_string_no_float_errors():
    assert Money.from_string("0.29 INR").minor == 29, (
        "0.29 INR must be 29. With float, 0.29 * 100 is 28.999999999999996 and int() gives 28. Split the text at '.' instead."
    )
    assert Money.from_string("1.15 INR").minor == 115, "1.15 must be exactly 115 minor units."
    assert Money.from_string("123456789.99 INR").minor == 12345678999, "Big amounts must be exact too."


def test_from_string_bad():
    for bad in ("12.505 INR", "12,50 INR", "abc INR", "12.50", "12.50  INR", "12.50 inr", "1.2.3 INR", ". INR", "12. INR", "+5 INR", "- 5 INR"):
        try:
            got = Money.from_string(bad)
        except ValueError:
            continue
        pytest.fail(
            f"from_string({bad!r}) was accepted (minor={got.minor}). Expect exactly '<digits>[.<1-2 digits>] <CUR>' "
            "with one space; raise ValueError for anything else."
        )


def test_from_string_respects_subclass():
    class Rupees(Money):
        pass

    assert type(Rupees.from_string("1 INR")) is Rupees, "from_string must use cls(...), so a subclass gets its own type."


def test_add_and_subtract_new_objects():
    a = Money.from_string("12.50 INR")
    b = a.add(Money(75, "INR"))
    assert (b.minor, b.currency) == (1325, "INR"), "12.50 + 0.75 = 13.25."
    assert a.minor == 1250, "add must return a NEW Money and leave a unchanged."
    c = a.subtract(Money(2000, "INR"))
    assert c.minor == -750, "subtract may go below 0."
    assert b is not a and c is not a, "Return new objects."


def test_mismatch_error():
    a = Money(1250, "INR")
    with pytest.raises(CurrencyMismatchError) as info:
        a.add(Money(100, "USD"))
    err = info.value
    assert (err.left, err.right) == ("INR", "USD"), "The error stores left (self's currency) and right (other's)."
    assert str(err) == "cannot combine INR and USD", "Message: 'cannot combine {left} and {right}'."
    assert isinstance(err, ValueError), "CurrencyMismatchError must inherit from ValueError."
    with pytest.raises(CurrencyMismatchError):
        a.subtract(Money(1, "EUR"))


def test_add_needs_money():
    a = Money(100, "INR")
    for bad in (5, 1.5, "1 INR"):
        with pytest.raises(TypeError):
            a.add(bad)


def test_times():
    assert Money(250, "INR").times(3).minor == 750, "times(3) multiplies the minor units."
    assert Money(250, "INR").times(-1).minor == -250, "A negative factor is fine."
    with pytest.raises(TypeError):
        Money(250, "INR").times(1.5)


def test_split_exact():
    parts = Money(1000, "INR").split(3)
    assert [p.minor for p in parts] == [334, 333, 333], "1000 into 3 parts: 334, 333, 333 (larger parts first)."
    assert all(p.currency == "INR" for p in parts), "Each part keeps the currency."
    assert [p.minor for p in Money(10, "INR").split(4)] == [3, 3, 2, 2], "10 into 4: 3, 3, 2, 2. The parts must add up exactly."
    assert [p.minor for p in Money(5, "INR").split(1)] == [5], "split(1) gives one part, the whole amount."
    assert [p.minor for p in Money(2, "INR").split(5)] == [1, 1, 0, 0, 0], "More parts than paise: some parts are 0."


def test_split_bad():
    for bad in (0, -2, 2.0):
        with pytest.raises(ValueError):
            Money(100, "INR").split(bad)


def test_format():
    assert Money(1250, "INR").format() == "12.50 INR", "Always 2 digits after the point."
    assert Money(7, "EUR").format() == "0.07 EUR", "7 paise is 0.07: pad the fraction with a zero."
    assert Money(-305, "USD").format() == "-3.05 USD", "Negative: a minus sign in front. Careful: -305 // 100 is -4 in Python."
    assert Money(-5, "USD").format() == "-0.05 USD", "Also for amounts below 1."
    assert Money(0, "INR").format() == "0.00 INR", "Zero is 0.00."


def test_repr():
    assert repr(Money(1250, "INR")) == "Money(1250, 'INR')", "__repr__ returns exactly Money(1250, 'INR')."
