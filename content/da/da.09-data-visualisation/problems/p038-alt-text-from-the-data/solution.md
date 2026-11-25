## Approach

`max` and `min` with a `key` return the first element among equals, which is exactly the tie rule of the problem. The numbers come from the figure, so the text always describes what is drawn.

## Code

```python
def alt_text(fig, what, by):
    pairs = bar_values(fig.axes[0])
    hi = max(pairs, key=lambda p: p[1])
    lo = min(pairs, key=lambda p: p[1])
    return f"Bar chart of {what} by {by}. Highest: {hi[0]} ({hi[1]:,.0f}). Lowest: {lo[0]} ({lo[1]:,.0f})."
```

## Complexity

O(n).

## Another way

Add the share of the total ("Airport (4,210, 52% of the total)") when the audience asks "how big is big?". Keep alt text to one or two sentences: long descriptions belong in a caption or a data table.
