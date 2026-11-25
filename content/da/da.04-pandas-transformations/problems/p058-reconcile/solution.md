## Approach

Sum the parts, subtract the total, round to cents. Money sums carry float noise (`0.1` has no exact binary form), so
an exact comparison would fail on correct data; a tolerance of one cent is the business meaning of "equal".
`round` of a tiny negative number gives `-0.0`, which prints as a confusing minus sign; adding `0.0` normalises it.
In strict mode the message names the check and shows the three numbers, so the reader knows what to look at.

## Code

```python
import pandas as pd


def reconcile(parts, total, label="", tol=0.01, strict=False):
    s = float(pd.Series(parts).sum())
    diff = round(s - total, 2) + 0.0
    ok = abs(diff) <= tol
    if strict and not ok:
        raise ValueError(f"{label}: parts={s:,.2f} total={total:,.2f} diff={diff:,.2f}")
    return bool(ok), diff
```

## Complexity

O(n) for the sum.

## Another way

`math.isclose(s, total, abs_tol=tol)` gives the same `ok` without rounding. The chapter's version also prints an
`[ok]`/`[MISMATCH]` line for every check, which makes a long analysis easy to read in a notebook; returning the values
instead makes the function easy to test and to use in an `assert`.
