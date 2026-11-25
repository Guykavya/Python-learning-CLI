## Approach

Each fault is one line of the original: `df.tail(3)` (window), `set_ylim(bottom=min * 0.95)` (baseline), a missing `set_ylabel` (unit), a title with no data (claim). Fix all four and derive the title **from the data**, so it cannot disagree with the chart.

## Code

```python
import matplotlib.pyplot as plt


def revenue_chart(df):
    first, last = df["revenue"].iloc[0], df["revenue"].iloc[-1]
    pct = round(abs(last / first - 1) * 100)
    word = "grew" if last >= first else "fell"
    start, end = df["date"].iloc[0].strftime("%b %Y"), df["date"].iloc[-1].strftime("%b %Y")
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["revenue"])
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Revenue (USD)")
    ax.set_title(f"Revenue {word} {pct}% from {start} to {end}")
    return fig
```

## Complexity

O(n).

## Another way

Keep the bars but plot all 24: the baseline is then honest too. For many months a line is easier to read.

## Note

A title is an assertion. Computing it from the data is the cheapest guarantee that it stays true when the data change.
