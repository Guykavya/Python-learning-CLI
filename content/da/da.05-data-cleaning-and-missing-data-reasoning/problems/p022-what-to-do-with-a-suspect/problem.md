# What to do with a suspect

Chapter section 6.5. Once a rule has flagged suspects you must choose: keep them, remove them, cap them, or only flag
them. The choice moves the **mean** a lot and the **median** very little. Seeing that in numbers is the point of this
problem.

Write `outlier_strategies(s, flags)`:

- `s` is a numeric Series (it may contain missing values); `flags` is a Boolean Series with the same index: `True` marks
  a suspect.
- Return a dict with four keys, each a dict with the `mean` and `median` (plain `float`) of the values **after** that
  strategy. Missing values are skipped by the statistics, as usual.

| key | what happens to the flagged values |
|---|---|
| `"keep"` | nothing: statistics of all of `s` |
| `"remove"` | they are dropped: statistics of the unflagged values only |
| `"cap"` | they are replaced by the nearest **IQR fence** (a value above the upper fence becomes the upper fence, a value below the lower fence becomes the lower fence); unflagged values never change |
| `"flag_only"` | nothing changes, so the same numbers as `"keep"`, plus the extra key `"n_flagged"` (an `int`) |

The fences come from **all** non-missing values of `s`: `Q1 - 1.5 * IQR` and `Q3 + 1.5 * IQR`, with the default
`s.quantile` (linear interpolation). A flagged value that is already inside the fences is not changed by `"cap"`.

Do not change `s` or `flags`.

## Example

```python
import pandas as pd

s = pd.Series([1, 2, 3, 4, 100])
flags = s > 50
print(outlier_strategies(s, flags))
```

```text
{'keep': {'mean': 22.0, 'median': 3.0}, 'remove': {'mean': 2.5, 'median': 2.5}, 'cap': {'mean': 3.4, 'median': 3.0}, 'flag_only': {'mean': 22.0, 'median': 3.0, 'n_flagged': 1}}
```

Here `Q1 = 2`, `Q3 = 4`, `IQR = 2`, so the upper fence is `7`: capping turns `100` into `7`, and the mean becomes
`(1 + 2 + 3 + 4 + 7) / 5 = 3.4`.
