## Approach

`duplicated(keep="first")` marks the repeats; the rows that are not marked are the first copies. Counting the marks
gives exactly the number of rows removed, which is what the change log of problem 1 wants. Nothing else is needed: the
method already compares **all** columns, treats missing values as equal, and keeps the index labels.

## Code

```python
import pandas as pd


def drop_exact_duplicates(df):
    repeat = df.duplicated(keep="first")
    return df[~repeat].copy(), int(repeat.sum())
```

## Complexity

O(n x c) to hash the rows (n rows, c columns).

## Another way

`clean = df.drop_duplicates()` and `n = len(df) - len(clean)`. Both are the same operation. Use the first form when you
also want to *look at* the repeats (`df[repeat]`) before removing them, and `keep=False` to see every member of a
duplicate group, including the first copy.
