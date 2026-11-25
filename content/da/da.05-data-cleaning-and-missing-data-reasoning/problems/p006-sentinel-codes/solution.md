## Approach

For each column named in `codes`, build the Boolean mask "is one of the codes", count it, and `mask` those cells to
missing. Counting *before* masking is what makes the log honest: the count is the number of cells that **were codes**,
not the number of missing cells afterwards (which would also include the values that were already missing). Working on a
copy keeps the raw table intact (rule 1 of the chapter).

## Code

```python
import pandas as pd


def replace_sentinels(df, codes):
    out = df.copy()
    counts = {}
    for col, values in codes.items():
        hit = out[col].isin(values)
        counts[col] = int(hit.sum())
        out[col] = out[col].mask(hit)
    return out, counts
```

## Complexity

O(n) per column listed in `codes` (one `isin`, one `mask`).

## Another way

`df[col].replace(values, np.nan)` also works and is shorter, but then you have to count separately. The chapter's
better idea is to describe what is **valid** (`age.where(age.between(18, 75))`) instead of listing the invalid values,
because the next export may use a code you have never seen. A list of codes is right when the codes are documented
(a codebook says `999 = no answer`); a range rule is right when they are not.
