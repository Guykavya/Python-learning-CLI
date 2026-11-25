## Approach

`transform("median")` gives every row the median of its own category, with the input's index. `fillna(series)` fills
each gap from the same label of that Series, so a known price is never touched. A category with no known price has a
missing median, so its gaps stay missing; `count()` per category (known values only) finds those categories.

## Code

```python
import pandas as pd


def fill_price_by_category(products):
    median = products.groupby("category")["list_price"].transform("median")
    filled = products.assign(list_price=products["list_price"].fillna(median))
    known = products.groupby("category")["list_price"].count()
    unfilled = sorted(known[known == 0].index.tolist())
    return filled, unfilled
```

## Complexity

O(n log n) at most for the medians; the fill and the counts are O(n).

## Another way

`filled["list_price"].isna()` after filling marks the products that still have no price;
`sorted(filled.loc[that_mask, "category"].unique())` gives the same `unfilled` list. Whether a group-median fill is an
honest choice at all is a cleaning decision discussed in da.05.
