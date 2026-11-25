## Approach

Normalise the tokens the same way as the data (strip, lower case) and compare through `isin`. Build a mask per text
column and use `mask` to blank those cells. Restricting the mask to `notna()` values keeps the count honest: a value
that was already missing is not a conversion. Numeric and datetime columns cannot contain these words, so they are
skipped and get a `0`.

## Code

```python
import pandas as pd


def to_missing(df, tokens=("", "NA", "n/a", "-")):
    out = df.copy()
    words = {t.strip().lower() for t in tokens}
    counts = {}
    for col in out.columns:
        s = out[col]
        if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s):
            counts[col] = 0
            continue
        hit = s.notna() & s.astype(str).str.strip().str.lower().isin(words)
        out[col] = s.mask(hit)
        counts[col] = int(hit.sum())
    return out, counts
```

## Complexity

O(rows x text columns). Each column is scanned a constant number of times.

## Another way

`df.replace(r"^\s*(NA|n/a|-)?\s*$", np.nan, regex=True)` does the job in one call, but one regex for every token is
harder to read and to extend. `pd.read_csv(..., na_values=[...])` can do it at load time for a file, which is the best
place when you control the loading.
