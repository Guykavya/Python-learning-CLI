## Approach

Within-stratum differences remove the effect of the stratum variable; weighting by stratum size gives a single summary that describes the whole (usable) population. A stratum without both groups cannot contribute and is reported, so the reader knows part of the data did not take part.

## Code

```python
import numpy as np


def adjusted_diff(df, treat, outcome, by):
    diffs, sizes, skipped = [], [], []
    for name, g in df.groupby(by):
        t = g.loc[g[treat].astype(bool), outcome]
        c = g.loc[~g[treat].astype(bool), outcome]
        if t.empty or c.empty:
            skipped.append(name)
            continue
        diffs.append(t.mean() - c.mean())
        sizes.append(len(g))
    if not diffs:
        raise ValueError("no stratum has both treated and untreated rows")
    return float(np.average(diffs, weights=sizes)), sorted(skipped)
```

## Complexity

O(n).

## Another way

Regression adjustment (problem 31) does the same job with several confounders at once and continuous ones. Stratification only works when you can make strata that are both few and well populated, and only for **measured** confounders.
