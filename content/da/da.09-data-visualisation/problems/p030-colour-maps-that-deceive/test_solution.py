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

import matplotlib

from solution import is_monotone_lightness, luminance_profile, pick_sequential


def test_profile_shape_and_range():
    lum = luminance_profile("viridis", 32)
    assert isinstance(lum, np.ndarray) and lum.shape == (32,), f"one luminance per sampled colour: shape (32,), got {getattr(lum, 'shape', None)}."
    assert 0 <= lum.min() and lum.max() <= 1, "luminance lies between 0 and 1."


def test_profile_values():
    lum = luminance_profile("viridis")
    assert lum[0] == pytest.approx(0.08, abs=0.02) and lum[-1] == pytest.approx(0.87, abs=0.02), (
        f"viridis goes from dark (about 0.08) to light (about 0.87), got {lum[0]:.2f} to {lum[-1]:.2f}: use RGB only and the weights 0.2126, 0.7152, 0.0722.")


@pytest.mark.parametrize("name", ["viridis", "cividis", "Blues", "Greys", "magma", "plasma"])
def test_honest_maps(name):
    assert is_monotone_lightness(name) is True, f"{name} gets steadily lighter or darker: it is monotone."


@pytest.mark.parametrize("name", ["jet", "rainbow", "hsv", "turbo"])
def test_deceiving_maps(name):
    assert is_monotone_lightness(name) is False, f"{name} changes direction in lightness: it creates false boundaries."


def test_pick_sequential():
    assert pick_sequential(["jet", "rainbow", "viridis", "Blues"]) == "viridis", "return the FIRST honest map of the list."
    assert pick_sequential(["jet", "hsv"]) is None, "when no map in the list is honest, return None."
    assert pick_sequential([]) is None


def test_reversed_maps_are_also_monotone():
    assert is_monotone_lightness("viridis_r") is True, "a reversed honest map is still honest."
