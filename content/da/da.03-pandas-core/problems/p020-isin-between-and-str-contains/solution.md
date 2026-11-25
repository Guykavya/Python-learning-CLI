## Approach

Three masks joined with `&`. `isin(categories)` is the readable form of a chain of `==` joined with `or`. `between(lo, hi)` includes both ends by default (`inclusive="both"`). `str.contains` returns a missing value for a missing name, and a mask with a missing value cannot filter, so `na=False` says "no match". `case=False` ignores case, and `regex=False` makes the word plain text so `c++` or `(x)` cannot break the pattern.

## Code

```python
import pandas as pd


def filter_products(df, categories, lo, hi, word):
    mask = (
        df["category"].isin(categories)
        & df["price"].between(lo, hi)
        & df["name"].str.contains(word, case=False, na=False, regex=False)
    )
    return df[mask]
```

## Complexity

O(n) for each of the three masks.

## Another way

`df["name"].str.lower().str.contains(word.lower(), na=False, regex=False)` gives the same result in two steps. For several words use a regex with `|` and `re.escape` on each word.
