import numpy as np
import pandas as pd
import pytest

from solution import xl_round


def test_halves_go_away_from_zero():
    assert xl_round(2.5) == 3.0 and xl_round(3.5) == 4.0 and xl_round(0.5) == 1.0, "Python's `round` rounds half to even (2, 4, 0); Excel rounds halves away from zero."
    assert xl_round(-2.5) == -3.0 and xl_round(-0.5) == -1.0, "also for negative numbers: -2.5 becomes -3."


def test_the_float_that_is_not_exactly_a_half():
    assert xl_round(1.005, 2) == 1.01, "the float 1.005 is stored as 1.00499...; Excel looks at 15 digits, sees 1.005 and rounds up to 1.01."
    assert xl_round(0.125, 2) == 0.13 and xl_round(2.675, 2) == 2.68 and xl_round(0.285, 2) == 0.29, "0.125, 2.675 and 0.285 all round up in Excel."


def test_other_digits_and_negative_places():
    assert xl_round(3.14159, 3) == 3.142 and xl_round(1234.5678, 1) == 1234.6, "ordinary rounding."
    assert xl_round(1250, -2) == 1300.0 and xl_round(-1250, -2) == -1300.0 and xl_round(1249, -2) == 1200.0, "n < 0 rounds to hundreds."
    assert xl_round(7) == 7.0 and xl_round(7.4) == 7.0, "default n = 0."


def test_result_is_a_float_and_differs_from_python():
    assert type(xl_round(2.5)) is float, "return a float."
    assert round(1.005, 2) == 1.0 and xl_round(1.005, 2) != round(1.005, 2), "(check) Python's round(1.005, 2) is 1.0."
