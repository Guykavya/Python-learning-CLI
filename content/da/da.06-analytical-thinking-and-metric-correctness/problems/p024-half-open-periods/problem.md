# Half-open periods

Chapter section 8.2. A period is **start included, end excluded**: `start <= t < end`. February is
`>= 2025-02-01` and `< 2025-03-01`. Two months then join with no gap and no overlap, and the afternoon of the last day
is never lost.

Write `in_period(s, start, end)`.

- `s` is a pandas Series of timestamps (it may contain `NaT`, "not a time").
- `start` and `end` are timestamps or date texts such as `"2025-02-01"`.
- Return a Series of `True` / `False` with **the same index** as `s`: `True` exactly when `start <= t < end`.
- A timestamp exactly at `start` is **in**; exactly at `end` is **out**; `NaT` is **out** (`False`, not missing).
- Do not change `s`.

## Example

```python
import pandas as pd

s = pd.Series(pd.to_datetime(["2025-01-31 23:59:59", "2025-02-01 00:00:00", "2025-02-28 23:59:59",
                              "2025-03-01 00:00:00", None]))
print(in_period(s, "2025-02-01", "2025-03-01").tolist())
```

```text
[False, True, True, False, False]
```
