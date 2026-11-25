## Approach

A join row is one pair (row of `a`, row of `b`) with equal keys. So the row count is the sum over key values of
`n_a * n_b`. `Counter` of the key tuples gives both counts; the missing value is turned into `None` so that two missing
keys are equal (as in pandas).

## Code

```python
from collections import Counter

import pandas as pd


def _counts(df, cols):
    counter = Counter()
    for row in df[cols].itertuples(index=False, name=None):
        counter[tuple(None if pd.isna(v) else v for v in row)] += 1
    return counter


def rows_after_join(a, b, key):
    cols = [key] if isinstance(key, str) else list(key)
    ca, cb = _counts(a, cols), _counts(b, cols)
    return sum(n * cb[k] for k, n in ca.items())
```

## Complexity

O(n + m) time and O(distinct keys) memory, against O(rows after the join) for the real merge.

## Another way

`a.groupby(key, dropna=False).size()` and the same for `b`, multiplied after an `align`/`reindex`, does it in pandas; the
`Counter` version shows the idea in plain Python and avoids index alignment surprises.
