import pytest
from solution import n_for_margin, n_for_proportion


def test_mean_hand_values():
    assert n_for_margin(20, 2) == 385, "(1.96 * 20 / 2)^2 = 384.1: round UP to 385 (rounding down gives a margin slightly too wide)."
    assert n_for_margin(10, 1, level=0.99) == 664, "99% needs z = 2.576: (2.576 * 10)^2 = 663.5 -> 664."


def test_proportion_hand_values():
    assert n_for_proportion(0.03) == 1068, "1.96^2 * 0.25 / 0.03^2 = 1067.1 -> 1068."
    assert n_for_proportion(0.05, p=0.1) == 139, "1.96^2 * 0.09 / 0.05^2 = 138.3 -> 139."


def test_integers_and_monotonic():
    assert isinstance(n_for_margin(5, 1), int) and isinstance(n_for_proportion(0.1), int)
    assert n_for_margin(5, 0.5) > n_for_margin(5, 1), "A smaller margin needs more data."
    assert 3.8 < n_for_margin(5, 0.5) / n_for_margin(5, 1) < 4.2, "Half the margin needs about four times the data."


@pytest.mark.parametrize("f", [lambda: n_for_margin(5, 0), lambda: n_for_proportion(-0.1)])
def test_bad_margin(f):
    with pytest.raises(ValueError):
        f()
