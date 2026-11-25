## Approach

The three questions are three set operations. `np.setdiff1d(a, b)` gives the sorted unique values of `a` that are not in `b`; `np.intersect1d(a, b)` the sorted unique values in both. Both remove duplicates and sort for you, and both keep the dtype of their inputs, so the repeated purchases in the data and the string ids need no special handling.

## Code

```python
import numpy as np


def customer_changes(jan_ids, feb_ids):
    jan = np.asarray(jan_ids)
    feb = np.asarray(feb_ids)
    new = np.setdiff1d(feb, jan)
    lost = np.setdiff1d(jan, feb)
    kept = np.intersect1d(jan, feb)
    return new, lost, kept
```

## Complexity

O((n + m) log(n + m)): the set functions sort internally.

## Another way

With masks: `u_feb = np.unique(feb)`, then `new = u_feb[~np.isin(u_feb, jan)]` and `kept = u_feb[np.isin(u_feb, jan)]`. That is what you need when you want the *rows* of a table (not only the ids), for example "all February purchases by new customers": `feb_rows[~np.isin(feb, jan)]`. In pandas (da.04) the same questions are answered with a merge with `indicator=True`.
