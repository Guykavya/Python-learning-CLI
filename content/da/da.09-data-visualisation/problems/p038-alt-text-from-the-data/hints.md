## Hint 1

Which function gives you the `(label, value)` pairs? Once you have them, what built-in finds the largest and the smallest by value, and what happens when two are equal?

## Hint 2

```text
pairs = bar_values(fig.axes[0])
hi = max(pairs, key=value); lo = min(pairs, key=value)      # max/min return the FIRST of equals
f"Bar chart of {what} by {by}. Highest: {hi[0]} ({hi[1]:,.0f}). Lowest: {lo[0]} ({lo[1]:,.0f})."
```
