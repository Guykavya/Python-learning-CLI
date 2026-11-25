## Approach

`barh(..., left=L)` starts each bar at `L` instead of 0. Negative lefts put bars on the left of zero. The neutral bar is centred: it starts at `-n/2` and is `n` wide.
A zero-width bar is a valid `Rectangle`; keeping it keeps the structure the same for every question.

## Code

```python
import matplotlib.pyplot as plt


def likert_bars(counts):
    pct = counts.div(counts.sum(axis=1), axis=0) * 100
    cols = list(pct.columns)
    sd, d, n, a, sa = (pct[c].to_numpy() for c in cols)
    half = n / 2
    lefts = [-(sd + d + half), -(d + half), -half, half, half + a]
    widths = [sd, d, n, a, sa]
    questions = [str(q) for q in pct.index]
    fig, ax = plt.subplots()
    for c, left, w in zip(cols, lefts, widths):
        ax.barh(questions, w, left=left, label=str(c))
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Share of answers (%)")
    ax.legend()
    return fig
```

## Complexity

O(questions x 5).

## Another way

Compute the left edges with a cumulative sum: `starts = np.cumsum(widths, axis=0) - widths - (sd + d + half)`. The explicit formula is easier to read.

## Note

A different colour for each side (two reds, grey, two blues) helps the reader; the problem tests the geometry only.
