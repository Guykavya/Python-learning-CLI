## Approach

Three problems, three causes:

1. **`df[df["qty"] < 0]["qty"] = 0`** is chained assignment: the first `[]` builds a temporary frame, the second sets a value in it, and the temporary is thrown away. In pandas 3 the original is never changed and a `ChainedAssignmentError` warning is raised. The fix is one `.loc[rows, column] = value`.
2. **`df["price"][i] = round(...)`** is chained too (`df["price"]` is a temporary Series), and it also assumes the labels are `0..n-1`. The whole column can be rounded in one vectorised call, which handles missing values and any index.
3. **The loop** does a Python-level step per row. `Series.round(2)` runs in compiled code.

And the function should not modify its argument: work on `df.copy()` (cheap under Copy-on-Write) and return the copy.

## Code

```python
def clean(df):
    out = df.copy()
    out.loc[out["qty"] < 0, "qty"] = 0
    out["price"] = out["price"].round(2)
    return out
```

## Complexity

O(n), with no Python loop.

## Another way

`df.assign(qty=df["qty"].clip(lower=0), price=df["price"].round(2))` is a pure expression with no in-place step at all. Keep the three symptoms as tests so the bug cannot come back.
