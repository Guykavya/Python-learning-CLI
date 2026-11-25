## Approach

`cut` takes **your** edges: `(0, 18]`, `(18, 40]`, `(40, 65]`, `(65, inf]`. By default the lowest edge is *excluded*, so age 0 would have no label; `include_lowest=True` fixes that. Negative ages and missing values fall outside every bin and stay missing. `qcut` takes the **number of groups** and computes the quartiles of the data as edges, so each group has about the same number of rows; its bins are right-closed with the lowest value included, so a value that sits exactly on an edge goes to the lower group.

## Code

```python
import numpy as np
import pandas as pd


def age_bands(s):
    return pd.cut(s, bins=[0, 18, 40, 65, np.inf],
                  labels=["youth", "adult", "middle", "senior"], include_lowest=True)


def spend_quartiles(s):
    return pd.qcut(s, q=4, labels=["Q1", "Q2", "Q3", "Q4"])
```

## Complexity

O(n log b) for `cut` (b edges) and O(n log n) for `qcut` (it needs sorted data to find the quartiles).

## Another way

`right=False` flips the rule to left-closed bins `[0, 18)`, `[18, 40)`, ... (age 18 would then be "adult"): choose the rule by what your labels *mean* and write it down. With many ties, `qcut(..., duplicates="drop")` removes equal edges, but then the labels must be given as a list of the right length or left as `None`.
