import pytest
from solution import classify

WORTH = "worth it: the whole interval is above the minimum effect"
NOT = "not worth it: the whole interval is below the minimum effect"
INC = "inconclusive: the interval contains the minimum effect"


@pytest.mark.parametrize("lo,hi,label,sig", [
    (0.06, 0.14, NOT, True),
    (-1.53, 4.53, INC, False),
    (0.14, 2.86, INC, True),
    (0.8, 2.0, WORTH, True),
    (-0.3, 0.2, NOT, False),
])
def test_chapter_rows(lo, hi, label, sig):
    assert classify(lo, hi) == (label, sig), f"[{lo}, {hi}] against the MEI 0.5: label {label!r}, significant = does the interval exclude 0?"


def test_significant_and_not_worth_it_exists():
    label, sig = classify(0.06, 0.14)
    assert sig and label.startswith("not worth it"), "A significant result can be too small to matter."


def test_boundaries_and_custom_mei():
    assert classify(0.5, 0.9)[0] == INC, "lo == mei is not above it."
    assert classify(0.1, 0.5)[0] == INC, "hi == mei is not below it."
    assert classify(0.0, 1.0, mei=2.0) == (NOT, False), "An interval touching 0 is not significant; use the mei argument."
