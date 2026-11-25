# Fix the pipeline that changes on every run

Chapter sections 12.2 and 12.4. A good cleaning step is **idempotent and deterministic**: the same input gives the
same output every time, and it never changes the caller's data behind their back. A colleague's step `clean` fails both
tests. The file `solution.py` already contains this code; fix it.

```python
import pandas as pd

LOG = []


def clean(df, log):
    """Grams to kilograms, fill missing prices with the median price, write one log line."""
    df["weight_g"] = df["weight_g"] / 1000
    n_missing = int(df["price"].isna().sum())
    df["price"] = df["price"].fillna(df["price"].median())
    out = df.rename(columns={"weight_g": "weight_kg"})
    LOG.append({"step": "clean", "rows": len(out), "price_filled": n_missing})
    return out[["item", "weight_kg", "price"]]
```

Required behaviour (the function's **contract**):

- Input `df`: columns `item`, `weight_g` (grams) and `price` (some missing).
- Output: a **new** frame with the columns `item`, `weight_kg` (`weight_g / 1000`) and `price` (every missing price
  replaced by the median of the **observed** prices), same index and row order as `df`.
- `df` is **never changed** (no new values, no converted units).
- One log line `{"step": "clean", "rows": <rows>, "price_filled": <how many prices were missing>}` is appended to the
  list `log` that the caller **passes in**, and **nowhere else**: no global list.
- Calling `clean(df, log)` twice with the same `df` gives two identical outputs.

## Symptoms the analyst reported

1. "I ran the cell twice and the weights are a thousand times smaller than before."
2. "After calling `clean`, my own table has no missing prices any more, and the column `weight_g` holds kilograms."
3. "`clean` seems to remember things between runs: its log keeps growing, and my own list stays empty."

## Example

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"item": ["a", "b", "c"], "weight_g": [1500.0, 250.0, 40.0], "price": [10.0, np.nan, 30.0]})
log = []
first = clean(df, log)
second = clean(df, log)
print(first["weight_kg"].tolist(), second["weight_kg"].tolist())
print(df["weight_g"].tolist(), int(df["price"].isna().sum()))
print(log)
```

```text
[1.5, 0.25, 0.04] [1.5, 0.25, 0.04]
[1500.0, 250.0, 40.0] 1
[{'step': 'clean', 'rows': 3, 'price_filled': 1}, {'step': 'clean', 'rows': 3, 'price_filled': 1}]
```
