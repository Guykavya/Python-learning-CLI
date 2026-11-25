## Approach

One boolean mask, two complementary selections. A row on the cutoff belongs to the test part, because on that day we already predict.

## Code

```python
import pandas as pd


def time_split(df, date_col, cutoff):
    col = df[date_col]
    cut = pd.Timestamp(cutoff) if pd.api.types.is_datetime64_any_dtype(col) else cutoff
    mask = col < cut
    return df[mask], df[~mask]
```

## Complexity

O(n).

## Another way

Sort by date and cut at a row number. A cutoff date is easier to explain and to repeat next month.
