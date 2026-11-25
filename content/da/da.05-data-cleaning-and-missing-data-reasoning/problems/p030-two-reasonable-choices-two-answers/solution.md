## Approach

Two answers to the same question, side by side. Way A: the mean of the answered rows, which pandas does by default.
Way B: fill each gap with the median income of its age band, then take the mean. `transform("median")` computes the
median of the observed values of each band (it skips missing values) and gives it back **aligned to every row**, so
`fillna` can use it directly. The difference between the two is the report line "the choice matters by this much".

## Code

```python
import numpy as np
import pandas as pd


def two_ways(df):
    band = pd.cut(df["age"], [-np.inf, 30, 45, np.inf], right=False)
    complete = df.groupby("city")["income"].mean()
    band_median = df.groupby(band, observed=True)["income"].transform("median")
    filled = df["income"].fillna(band_median).groupby(df["city"]).mean()
    complete.name = filled.name = "income"
    return {"complete": complete, "filled": filled, "max_diff": float((filled - complete).abs().max())}
```

## Complexity

O(n) for the two groupbys and the fill, plus O(n log n) for the medians.

## Another way

Fill with the group **mean** or with a regression on age (chapter 9.1). A group mean keeps the average of each band
but, like the median, fills every gap in the band with the same number, so the spread shrinks. A random draw from the
observed incomes of the band keeps the spread but needs a seed (chapter 9.5). Whatever you choose, keep the
complete-case answer next to it: if the two agree, the choice does not matter; if they differ, you owe the reader
both numbers and the reason (chapter 9.6).
