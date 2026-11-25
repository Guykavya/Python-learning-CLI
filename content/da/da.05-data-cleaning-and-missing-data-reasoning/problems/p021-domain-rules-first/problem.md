# Domain rules first

Chapter section 6.4. Before any statistical rule, write down what is **impossible** in your data: an age below 0 or above
120, a negative income. These rules need no distribution, are easy to explain, and are what a schema checks later.

Write `flag_impossible(df, rules)`:

- `rules` is a dict `{column: (low, high)}`. A value is **impossible** when it is below `low` or above `high`.
  The bounds themselves are allowed. A bound of `None` means "no limit on that side", so `(0, None)` only forbids
  negative values.
- Return a pair `(flags, counts)`:
  - `flags`: a DataFrame with the **same index** as `df` and one Boolean column per rule (same order as `rules`):
    `True` where the value is impossible.
  - `counts`: a dict `{column: number of True in that column}` with plain `int` values.
- A **missing** value is not impossible (it is a missing-data question, not a range question): it gives `False`.
- Do not change `df`. Columns of `df` that have no rule do not appear in `flags`.

## Example

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"age": [25, -3, 130, np.nan], "income": [50000.0, 0.0, -5.0, 120000.0]})
flags, counts = flag_impossible(df, {"age": (0, 120), "income": (0, None)})
print(flags)
print(counts)
```

```text
     age  income
0  False   False
1   True   False
2   True    True
3  False   False
{'age': 2, 'income': 1}
```

Row 2 breaks both rules. The income `0.0` is allowed (the bound is inclusive), and the missing age is not flagged.
