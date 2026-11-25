from pathlib import Path

import matplotlib.pyplot as plt

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _trend(df):
    monthly = df.groupby(df["date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum()
    years = df.groupby(df["date"].dt.year)["revenue"].sum()
    g = years.iloc[-1] / years.iloc[0] - 1
    title = f"Revenue {'grew' if g >= 0 else 'fell'} {round(abs(g) * 100)}% from {int(years.index[0])} to {int(years.index[-1])}"
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(monthly.index, monthly.values)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly revenue (USD)")
    ax.set_title(title)
    return fig, title, "Line chart of monthly revenue"


def _stores(df):
    t = df.groupby("store")["revenue"].sum().sort_values()
    title = f"{t.index[-1]} earns {t.iloc[-1] / t.iloc[0]:.1f} times as much as {t.index[0]}"
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh([str(s) for s in t.index], t.values)
    ax.set_xlim(left=0)
    ax.set_xlabel("Revenue (USD)")
    ax.set_ylabel("Store")
    ax.set_title(title)
    return fig, title, "Bar chart of revenue by store"


def _categories(df):
    t = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    title = f"{t.index[0]} is the largest category ({t.iloc[0] / t.sum() * 100:.0f}% of revenue)"
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar([str(c) for c in t.index], t.values)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue (USD)")
    ax.set_title(title)
    return fig, title, "Bar chart of revenue by category"


def _weekdays(df):
    daily = df.groupby("date")["revenue"].sum()
    by_day = daily.groupby(daily.index.day_of_week).mean().reindex(range(7))
    title = f"{DAYS[int(by_day.to_numpy().argmax())]} is the busiest weekday"
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(DAYS, by_day.values)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Average daily revenue (USD)")
    ax.set_title(title)
    return fig, title, "Bar chart of average daily revenue by weekday"


def make_figures(sales_df):
    out = []
    for name, build in (("trend", _trend), ("stores", _stores), ("categories", _categories), ("weekdays", _weekdays)):
        fig, title, kind = build(sales_df)
        out.append((name, fig, f"{kind}. {title}."))
    return out


def build_report(sales_df, folder):
    folder = Path(folder)
    files, lines = [], ["# Sales report", ""]
    figures = make_figures(sales_df)
    try:
        for name, fig, alt in figures:
            path = folder / f"{name}.png"
            fig.savefig(path, dpi=100)
            files.append(path)
            lines += [f"![{alt}]({name}.png)", ""]
    finally:
        for _, fig, _ in figures:
            plt.close(fig)
    report = folder / "report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    return files + [report]
