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

import matplotlib.colors

from solution import safe_pairs

DEUTAN = np.array([[0.625, 0.375, 0.0], [0.700, 0.300, 0.0], [0.0, 0.300, 0.700]])


def sep(c1, c2):
    a = np.clip(DEUTAN @ np.array(matplotlib.colors.to_rgb(c1)), 0, 1)
    b = np.clip(DEUTAN @ np.array(matplotlib.colors.to_rgb(c2)), 0, 1)
    return float(np.linalg.norm(a - b))


PALETTE = ["#d62728", "#2ca02c", "#E69F00", "#0072B2", "#009E73"]


def test_red_green_is_rejected_and_orange_blue_kept():
    got = safe_pairs(PALETTE[:2] + PALETTE[2:4], 0.5)
    assert ("#d62728", "#2ca02c") not in got, "red and green are only 0.43 apart for red-green colour blindness: reject at min_sep 0.5."
    assert ("#E69F00", "#0072B2") in got, "orange and blue stay about 1.03 apart: keep."


@pytest.mark.parametrize("min_sep", [0.2, 0.5, 0.8, 1.0, 1.5])
def test_matches_the_definition(min_sep):
    expected = [(PALETTE[i], PALETTE[j]) for i in range(len(PALETTE)) for j in range(i + 1, len(PALETTE)) if sep(PALETTE[i], PALETTE[j]) >= min_sep]
    assert safe_pairs(PALETTE, min_sep) == expected, f"min_sep={min_sep}: return every pair i<j with simulated separation >= min_sep, in order."


def test_no_pairs_when_the_limit_is_huge():
    assert safe_pairs(PALETTE, 10.0) == [], "no pair is 10 apart."


def test_pairs_are_unordered_and_unique():
    got = safe_pairs(PALETTE, 0.0)
    assert len(got) == 10, f"five colours make 10 pairs when nothing is rejected, got {len(got)}."
    assert all(a != b for a, b in got), "never pair a colour with itself."


def test_empty_and_single():
    assert safe_pairs([], 0.5) == [] and safe_pairs(["#000000"], 0.5) == [], "fewer than two colours: no pairs."
