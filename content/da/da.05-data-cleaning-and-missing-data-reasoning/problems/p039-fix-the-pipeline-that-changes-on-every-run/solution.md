## Approach

Three separate defects, one root cause: the function does not treat its input as **read-only** and keeps hidden state.

1. `df["weight_g"] = df["weight_g"] / 1000` assigns to the **caller's** frame. The next call divides the already
   converted numbers again (symptom 1) and the caller's table now holds kilograms in a column named `weight_g`
   (symptom 2).
2. `df["price"] = df["price"].fillna(...)` fills the caller's frame too. The second call would find no missing price
   and log `price_filled` of 0.
3. `LOG.append(...)` writes to a module-level list, so the function remembers across runs, and the list the caller
   passed in (`log`) is ignored (symptom 3).

The fix is to copy first, assign only to the copy, and use the `log` argument.

## Code

```python
import pandas as pd


def clean(df, log):
    out = df.copy()
    n_missing = int(out["price"].isna().sum())
    out["price"] = out["price"].fillna(out["price"].median())
    out["weight_kg"] = out["weight_g"] / 1000
    out = out[["item", "weight_kg", "price"]]
    log.append({"step": "clean", "rows": len(out), "price_filled": n_missing})
    return out
```

## Complexity

O(rows): one copy and two vectorised operations. The copy costs memory but buys correctness.

## Another way

Make the contract explicit with a test that runs the step twice and compares (as the tests of this problem do), or
`assert df.equals(df_before)` at the start of your own pipeline tests. Also possible: build the output in one
expression with `df.assign(weight_kg=..., price=...)[[...]]`, because `assign` returns a new frame.
