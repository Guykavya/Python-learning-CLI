## Approach

Clean first, then convert. `where(isin(ORDER))` turns every value outside the list into a missing value, so the
conversion to the categorical type has nothing to complain about. Counting rows that were present before and missing
after gives exactly the invalid ones. An ordered `CategoricalDtype` sorts by the category order, and missing values go
last by default; `kind="stable"` keeps the original order among equal sizes.

## Code

```python
import pandas as pd

ORDER = ["S", "M", "L", "XL"]


def sort_by_size(df):
    known = df["size"].where(df["size"].isin(ORDER))
    n_unknown = int((df["size"].notna() & known.isna()).sum())
    dtype = pd.CategoricalDtype(ORDER, ordered=True)
    out = df.assign(size=known.astype(dtype)).sort_values("size", kind="stable").reset_index(drop=True)
    return out, n_unknown
```

## Complexity

O(n log n) for the sort; the rest is O(n).

## Another way

Without a categorical, sort by a rank: `df.assign(r=df["size"].map({"S": 0, "M": 1, "L": 2, "XL": 3}))
.sort_values("r", kind="stable")`. It works for sorting, but the column does not know its order for `min`, `max`,
comparisons (`>= "M"`) or `groupby` on all sizes, which the categorical gives for free.
