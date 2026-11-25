import pytest

from conftest import make_sales
from solution import uses_future


@pytest.fixture(scope="module")
def s():
    return make_sales()["sales"]


def test_trailing_features_are_fine(s):
    assert uses_future(lambda x: x.shift(1).rolling(7).mean(), s, 400) is False, "a lagged trailing mean uses only the past."
    assert uses_future(lambda x: x.ewm(span=5).mean(), s, 400) is False, "an exponential moving average uses only the past."
    assert uses_future(lambda x: x.shift(7), s, 400) is False, "last week's value is known."


def test_look_ahead_is_caught(s):
    assert uses_future(lambda x: x.rolling(3, center=True).mean(), s, 400) is True, "a centred window uses tomorrow's value."
    assert uses_future(lambda x: x.shift(-1), s, 400) is True, "shift(-1) is tomorrow."
    assert uses_future(lambda x: x - x.mean(), s, 400) is True, "the mean of the whole series contains the future."


def test_nan_equals_nan(s):
    assert uses_future(lambda x: x.rolling(30).mean(), s, 5) is False, "at t = 5 both versions give NaN; that is not a change."
