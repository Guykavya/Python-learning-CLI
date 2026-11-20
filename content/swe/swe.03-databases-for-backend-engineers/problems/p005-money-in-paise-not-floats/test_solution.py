import pytest

from solution import order_total, to_paise


@pytest.mark.parametrize("text,paise", [("12.30", 1230), ("0", 0), ("1299", 129900), ("0.01", 1), ("19.99", 1999),
                                        (" 5.5 ", 550), ("0.10", 10), ("1000000.00", 100000000)])
def test_exact_amounts(text, paise):
    assert to_paise(text) == paise and isinstance(to_paise(text), int), f"to_paise({text!r}) should be {paise}."


def test_float_errors_do_not_appear():
    assert to_paise("19.99") == 1999, "19.99 * 100 is 1998.9999999999998 as a float: use Decimal."
    assert to_paise("0.10") + to_paise("0.20") == to_paise("0.30"), "In integer paise 10 + 20 == 30."
    assert to_paise("1.005") == 101, "1.005 is exactly 1.005 as a Decimal, so half-up gives 101 (floats give 100)."


@pytest.mark.parametrize("text,paise", [("12.345", 1235), ("0.005", 1), ("0.004", 0), ("2.675", 268), ("-1.005", -101),
                                        ("-0.004", 0), ("0.5", 50)])
def test_rounding_is_half_away_from_zero(text, paise):
    assert to_paise(text) == paise, f"{text} -> {paise}: round half away from zero, not banker's rounding."


@pytest.mark.parametrize("text", ["", "abc", "1,5", "nan", "inf", "-inf", "1.2.3", "12 30"])
def test_bad_text(text):
    with pytest.raises(ValueError):
        to_paise(text)


def test_order_total():
    assert order_total([(2, 25000), (1, 30000)]) == 80000
    assert order_total([]) == 0
    assert order_total([(3, 333)]) == 999
    assert isinstance(order_total([(1, 1)]), int)
