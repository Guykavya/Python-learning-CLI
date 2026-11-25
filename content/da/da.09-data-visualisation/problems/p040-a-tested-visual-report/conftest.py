import matplotlib
matplotlib.use("Agg")
import matplotlib.text
import numpy as np
import pandas as pd


def make_sales(seed=3, growth=0.12, stores=("Airport", "Campus", "Mall"), categories=("espresso", "pastry")):
    """Small BrewCo-like table: one row per date, store and category, 2023-01-01 .. 2024-12-31."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    t = np.arange(len(dates))
    rows = []
    for k, s in enumerate(stores):
        for c, base in zip(categories, (90, 50)):
            weekend = np.where(dates.day_of_week >= 5, 1.3, 1.0)
            units = rng.poisson(base * (1.5 - 0.25 * k) * (1 + growth * t / 365) * weekend)
            rows.append(pd.DataFrame({"date": dates, "store": s, "category": c, "units": units, "revenue": units * (3.2 if c == "espresso" else 3.8)}))
    return pd.concat(rows, ignore_index=True)


def lint_figure(fig, min_font=8.0, max_legend=7):
    fig.canvas.draw()
    issues = []
    for i, ax in enumerate(fig.axes):
        if ax.get_label() == "<colorbar>":
            continue
        name = f"axes[{i}]"
        if not ax.get_title():
            issues.append(f"{name}: no title")
        if (ax.lines or ax.patches or ax.collections) and not ax.get_xlabel() and not ax.get_ylabel():
            issues.append(f"{name}: no axis labels")
        if ax.patches and not ax.lines:
            heights = {round(p.get_height(), 6) for p in ax.patches}
            widths = {round(p.get_width(), 6) for p in ax.patches}
            limit = ax.get_xlim()[0] if (len(heights) == 1 and len(widths) > 1) else ax.get_ylim()[0]
            if limit > 0:
                issues.append(f"{name}: bar chart value axis starts at {limit:g}, not 0")
        legend = ax.get_legend()
        if legend is not None and len(legend.get_texts()) > max_legend:
            issues.append(f"{name}: legend has {len(legend.get_texts())} entries (more than {max_legend})")
    for t in fig.findobj(matplotlib.text.Text):
        if t.get_visible() and t.get_text().strip() and t.get_fontsize() < min_font:
            issues.append(f"text smaller than {min_font:g} pt")
            break
    return issues
