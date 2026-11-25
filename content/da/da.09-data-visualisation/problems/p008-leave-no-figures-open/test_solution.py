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

from pathlib import Path

from solution import render_all


def frame(n=3):
    return pd.DataFrame({"label": list("abcdefgh")[:n], "value": list(range(1, n + 1))})


def test_files_are_written_in_order(tmp_path):
    paths = render_all({"q1": frame(), "q2": frame(4)}, tmp_path)
    assert [p.name for p in paths] == ["q1.png", "q2.png"], f"return the paths in the order of the dict, got {[p.name for p in paths]}."
    assert all(isinstance(p, Path) and p.exists() and p.stat().st_size > 0 for p in paths), "every returned path must be a saved, non-empty file."


def test_no_figure_stays_open(tmp_path):
    render_all({f"c{i}": frame() for i in range(30)}, tmp_path)
    assert plt.get_fignums() == [], "each plt.subplots() keeps a figure alive until you close it; 200 of them fill memory. Close every figure."


def test_empty_input(tmp_path):
    assert render_all({}, tmp_path) == [], "no frames: no files and an empty list."
    assert plt.get_fignums() == []


def test_error_reaches_the_caller_but_figures_are_closed(tmp_path):
    frames = {"ok": frame(), "broken": pd.DataFrame({"label": ["a"]}), "later": frame()}
    with pytest.raises(KeyError):
        render_all(frames, tmp_path)
    assert plt.get_fignums() == [], "an error in the middle of the loop must not leave its figure open: use try/finally."
    assert (tmp_path / "ok.png").exists(), "figures finished before the error are kept."


def test_chart_content(tmp_path):
    seen = []
    orig = plt.close

    def spy(fig=None):
        if fig not in (None, "all"):
            seen.append([float(p.get_height()) for p in fig.axes[0].patches])
        return orig(fig) if fig is not None else orig()

    plt.close = spy
    try:
        render_all({"x": pd.DataFrame({"label": ["a", "b"], "value": [5, 7]})}, tmp_path)
    finally:
        plt.close = orig
    assert seen == [[5.0, 7.0]], f"draw the value column as bar heights, got {seen}."
