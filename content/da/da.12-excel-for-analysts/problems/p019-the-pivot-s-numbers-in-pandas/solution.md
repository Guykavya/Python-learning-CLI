## Approach

`pivot_table` builds the numbers and the margins; the explicit order reproduces Excel's case-insensitive sort; rounding to 2 decimals matches what is displayed (and what a pasted pivot would hold).

## Code

```python
import pandas as pd


def pivot_expected(orders):
    pt = orders.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum",
                            margins=True, margins_name="Grand Total", fill_value=0)
    rows = sorted([r for r in pt.index if r != "Grand Total"], key=str.lower) + ["Grand Total"]
    cols = sorted([c for c in pt.columns if c != "Grand Total"], key=str.lower) + ["Grand Total"]
    return pt.loc[rows, cols].round(2)
```

## Complexity

O(n).

## Another way

`pd.crosstab(index, columns, values=..., aggfunc="sum", margins=True)` gives the same table.
