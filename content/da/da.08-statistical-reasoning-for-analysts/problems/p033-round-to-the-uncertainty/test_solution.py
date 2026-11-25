import pytest
from solution import sig_round


@pytest.mark.parametrize("value,ref,expected", [
    (2577.616, 63, "2,578"),
    (2498.13, 5.9, "2,498.1"),
    (12.3456, 0.4, "12.35"),
    (1234567.891, 120, "1,234,568"),
    (0.03456, 0.004, "0.0346"),
])
def test_examples(value, ref, expected):
    assert sig_round(value, ref) == expected, f"ref {ref}: about two significant digits of the uncertainty (not a fixed 2 decimals)."


@pytest.mark.parametrize("ref", [0, float("nan"), float("inf")])
def test_no_usable_uncertainty(ref):
    assert sig_round(1234.56, ref) == "1,235", "ref 0 or not finite: a whole number with a thousands separator."


def test_negative_ref_and_negative_value():
    assert sig_round(-2577.6, -63) == "-2,578"


def test_returns_string():
    assert isinstance(sig_round(1.0, 0.1), str)
