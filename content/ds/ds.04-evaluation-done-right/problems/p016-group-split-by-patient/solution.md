## Approach

Hand the group labels to a group-aware splitter: it chooses whole groups for the test set.

## Code

```python
import numpy as np
from sklearn.model_selection import GroupShuffleSplit


def group_split(df, group_col, test_frac, seed):
    gss = GroupShuffleSplit(n_splits=1, test_size=test_frac, random_state=seed)
    train, test = next(gss.split(df, groups=df[group_col]))
    return np.sort(train), np.sort(test)
```

## Complexity

O(n).

## Another way

Choose a random subset of the unique group ids yourself and use `df[group_col].isin(chosen)`.
