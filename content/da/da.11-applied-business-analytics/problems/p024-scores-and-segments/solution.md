## Approach

Ranking breaks ties **by position** so every customer gets a distinct rank, and the quantile cut then makes equal-sized groups. (Customers with the same value can land in different scores: acceptable for a tied variable like frequency, and the chapter uses hand-made bins for it instead.)

## Code

```python
import pandas as pd


def score_quantile(s, higher_is_better=True, n=5):
    r = s.rank(method="first", ascending=higher_is_better)
    return pd.qcut(r, n, labels=list(range(1, n + 1))).astype(int)


def segment(r, f):
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / promising"
    if r <= 2 and f >= 3:
        return "At risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs attention"
```

## Complexity

O(n log n) for the rank.

## Another way

For a variable with only a few distinct values (orders per customer), define the bins by hand with `pd.cut(F, [0, 1, 2, 3, 5, inf], labels=[1, 2, 3, 4, 5])` so that equal values always get equal scores.
