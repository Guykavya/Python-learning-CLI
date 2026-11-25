import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")

from solution import contrast_ratio, passes_aa, rel_luminance


def test_luminance_extremes():
    assert rel_luminance("#000000") == pytest.approx(0.0), "black has luminance 0."
    assert rel_luminance("#ffffff") == pytest.approx(1.0), "white has luminance 1."
    assert rel_luminance("#ff0000") == pytest.approx(0.2126), "pure red: weight 0.2126 of the linear red channel."


def test_black_on_white_and_identity():
    assert contrast_ratio("#000000") == pytest.approx(21.0), "black on white is the maximum, 21."
    assert contrast_ratio("#336699", "#336699") == pytest.approx(1.0), "a colour on itself has ratio 1."


def test_ratio_is_symmetric():
    assert contrast_ratio("#0072B2", "#ffffff") == pytest.approx(contrast_ratio("#ffffff", "#0072B2")), "swapping foreground and background does not change the ratio."


def test_known_values():
    assert contrast_ratio("#777777") == pytest.approx(4.48, abs=0.01), "#777777 on white is about 4.48 (just below 4.5)."
    assert contrast_ratio("#555555") == pytest.approx(7.46, abs=0.01), "#555555 on white is 7.46."
    assert contrast_ratio("#F0E442") == pytest.approx(1.32, abs=0.01), "Okabe yellow on white is only 1.32."


def test_passes_aa():
    assert passes_aa("#555555") is True
    assert passes_aa("#777777") is False, "4.48 is just under 4.5: normal text fails."
    assert passes_aa("#777777", large=True) is True, "large text and graphics need only 3."
    assert passes_aa("#bbbbbb", large=True) is False, "light grey (1.92) fails even the large-text limit."
    assert passes_aa("#ffffff", "#000000") is True, "white on black passes."
