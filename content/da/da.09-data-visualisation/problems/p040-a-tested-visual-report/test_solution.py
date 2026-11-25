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

import re

from conftest import lint_figure, make_sales
from solution import build_report, make_figures

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
KINDS = {"trend": "Line chart of monthly revenue", "stores": "Bar chart of revenue by store",
         "categories": "Bar chart of revenue by category", "weekdays": "Bar chart of average daily revenue by weekday"}


def expected_titles(df):
    years = df.groupby(df["date"].dt.year)["revenue"].sum()
    g = years.iloc[-1] / years.iloc[0] - 1
    trend = f"Revenue {'grew' if g >= 0 else 'fell'} {round(abs(g) * 100)}% from {years.index[0]} to {years.index[-1]}"
    st = df.groupby("store")["revenue"].sum().sort_values()
    stores = f"{st.index[-1]} earns {st.iloc[-1] / st.iloc[0]:.1f} times as much as {st.index[0]}"
    ct = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    categories = f"{ct.index[0]} is the largest category ({ct.iloc[0] / ct.sum() * 100:.0f}% of revenue)"
    daily = df.groupby("date")["revenue"].sum()
    by_day = daily.groupby(daily.index.day_of_week).mean()
    weekdays = f"{DAYS[int(by_day.idxmax())]} is the busiest weekday"
    return {"trend": trend, "stores": stores, "categories": categories, "weekdays": weekdays}


@pytest.fixture(scope="module")
def sales():
    return make_sales()


def titles_of(figs):
    return {name: fig.axes[0].get_title() for name, fig, _ in figs}


def test_four_figures_in_order_and_each_passes_the_linter(sales):
    figs = make_figures(sales)
    assert [n for n, _, _ in figs] == ["trend", "stores", "categories", "weekdays"], "return the four figures in this order: trend, stores, categories, weekdays."
    for name, fig, _ in figs:
        assert lint_figure(fig) == [], f"{name}: every figure must pass the chart linter, problems: {lint_figure(fig)}."


def test_titles_are_computed_from_the_data(sales):
    figs = make_figures(sales)
    assert titles_of(figs) == expected_titles(sales), f"titles must state the numbers of the data: expected {expected_titles(sales)}, got {titles_of(figs)}."


def test_titles_follow_other_data():
    other = make_sales(seed=9, growth=-0.25, stores=("Mall", "Campus", "Airport"), categories=("pastry", "espresso"))
    figs = make_figures(other)
    exp = expected_titles(other)
    assert "fell" in exp["trend"], "(test data check) the declining table must make the trend title say 'fell'."
    assert titles_of(figs) == exp, f"a typed title would fail here: expected {exp}, got {titles_of(figs)}."


def test_chart_content(sales):
    figs = {n: f for n, f, _ in make_figures(sales)}
    assert figs["trend"].axes[0].get_ylim()[0] == 0, "the trend y axis starts at 0."
    w = figs["weekdays"].axes[0]
    w.figure.canvas.draw()
    assert [t.get_text() for t in w.get_xticklabels()] == DAYS, "weekday bars run Monday to Sunday."
    assert len(w.patches) == 7
    s = figs["stores"].axes[0]
    totals = sorted(sales.groupby("store")["revenue"].sum())
    assert [float(p.get_width()) for p in s.patches] == pytest.approx(totals), "store bars are ascending totals (smallest at the bottom)."
    c = figs["categories"].axes[0]
    cat_totals = sales.groupby("category")["revenue"].sum().sort_values(ascending=False)
    assert [float(p.get_height()) for p in c.patches] == pytest.approx(list(cat_totals.values)), "category bars are totals, largest first."


def test_alt_text(sales):
    for name, fig, alt in make_figures(sales):
        title = fig.axes[0].get_title()
        assert alt == f"{KINDS[name]}. {title}.", f"{name}: alt text must be '<kind>. <title>.', got {alt!r}."


def test_report_files(sales, tmp_path):
    out = build_report(sales, tmp_path)
    assert [p.name for p in out] == ["trend.png", "stores.png", "categories.png", "weekdays.png", "report.md"], f"return the four PNG paths and then report.md, got {[p.name for p in out]}."
    for p in out[:4]:
        assert p.read_bytes()[:4] == b"\x89PNG", f"{p.name} must be a PNG file."
    assert plt.get_fignums() == [], "build_report must leave no figure open."


def test_report_markdown(sales, tmp_path):
    build_report(sales, tmp_path)
    lines = (tmp_path / "report.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# Sales report", f"the first line is the title '# Sales report', got {lines[0]!r}."
    imgs = re.findall(r"^!\[(.+?)\]\((.+?\.png)\)$", "\n".join(lines), re.M)
    assert [f for _, f in imgs] == ["trend.png", "stores.png", "categories.png", "weekdays.png"], f"four image lines in order, got {imgs}."
    alts = {n: a for n, _, a in make_figures(sales)}
    assert [a for a, _ in imgs] == [alts[n] for n in ("trend", "stores", "categories", "weekdays")], "each image's alt text is the figure's alt text."
