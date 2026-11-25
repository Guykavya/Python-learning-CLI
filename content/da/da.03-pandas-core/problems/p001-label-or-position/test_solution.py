import pandas as pd
import pytest

from solution import nth_price, price_of


def shop():
    return pd.Series([10.0, 20.0, 30.0, 40.0], index=[102, 7, 0, 55])


def test_price_of_uses_the_label():
    s = shop()
    assert price_of(s, 7) == 20.0, "price_of(s, 7) must find the row LABELLED 7 (20.0): use s.loc[label]."
    assert price_of(s, 0) == 30.0, "label 0 is the third row here (30.0), not the first: labels are not positions."


def test_price_of_unknown_label_raises_keyerror():
    with pytest.raises(KeyError):
        price_of(shop(), 1)


def test_nth_price_uses_the_position():
    s = shop()
    for n, want in [(0, 10.0), (1, 20.0), (3, 40.0), (-1, 40.0), (-2, 30.0)]:
        try:
            got = nth_price(s, n)
        except KeyError:
            pytest.fail("nth_price(s, %d) raised KeyError: s[n] is a LABEL lookup when the index is integers. Use s.iloc[n]." % n)
        assert got == want, "nth_price(s, %d) should be %s (position %d), got %s. Use s.iloc[n], not s[n]." % (n, want, n, got)


def test_returns_python_float():
    s = shop()
    assert type(price_of(s, 7)) is float, "return float(...), not a numpy scalar."
    assert type(nth_price(s, 0)) is float, "return float(...), not a numpy scalar."


def test_default_index_both_agree():
    s = pd.Series([1.5, 2.5, 3.5])
    assert price_of(s, 1) == 2.5 and nth_price(s, 1) == 2.5, "with the default index 0..n-1 label and position are the same."


def test_input_not_changed():
    s = shop()
    before = s.copy()
    price_of(s, 7)
    nth_price(s, 2)
    pd.testing.assert_series_equal(s, before, obj="the input Series")
