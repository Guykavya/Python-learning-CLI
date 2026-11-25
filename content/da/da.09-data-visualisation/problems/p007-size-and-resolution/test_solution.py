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

import matplotlib.image as mpimg
from pathlib import Path

from solution import save_png


def make_fig():
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot([0, 1], [0, 1])
    return fig


def test_pixel_size_is_figsize_times_dpi(tmp_path):
    out = save_png(make_fig(), tmp_path / "c.png", dpi=50)
    img = mpimg.imread(out)
    assert img.shape[:2] == (150, 200), f"4x3 inches at 50 dpi is 200x150 pixels (rows, columns = 150, 200), got {img.shape[:2]} (no bbox_inches='tight')."


def test_default_dpi(tmp_path):
    out = save_png(make_fig(), tmp_path / "c.png")
    assert mpimg.imread(out).shape[:2] == (300, 400), "the default dpi is 100: 4x3 inches is 400x300 pixels."


def test_png_signature_and_return_type(tmp_path):
    out = save_png(make_fig(), str(tmp_path / "c.png"), dpi=40)
    assert isinstance(out, Path), "return a pathlib.Path (even if you were given a str)."
    assert out.read_bytes()[:4] == b"\x89PNG", "a .png file must contain PNG data."


def test_svg(tmp_path):
    out = save_png(make_fig(), tmp_path / "c.svg", dpi=10)
    text = out.read_text(encoding="utf-8")
    assert "<svg" in text, "a .svg file must contain SVG markup."


def test_other_suffix_is_refused(tmp_path):
    with pytest.raises(ValueError, match="unsupported format"):
        save_png(make_fig(), tmp_path / "c.gif")
    assert list(tmp_path.iterdir()) == [], "check the suffix before writing: no file should be left behind."
