## Approach

The interval, not the point estimate, decides. "Not supported" has two forms: the effect goes the other way, or the data rule out any effect big enough to matter. Everything else is honestly "inconclusive": the data are compatible with both an important effect and no effect.

## Code

```python
import pandas as pd


def _verdict(r):
    lo, hi, null, m = r["ci_low"], r["ci_high"], r["null"], r["margin"]
    if r["direction"] == "up":
        supported, opposite = lo > null, hi < null
    else:
        supported, opposite = hi < null, lo > null
    if supported:
        return "supported"
    if opposite or (null - m <= lo and hi <= null + m):
        return "not supported"
    return "inconclusive"


def evidence_table(results):
    rows = [{"hypothesis": r["hypothesis"], "estimate": r["estimate"],
             "CI": f"{r['ci_low']:.2f} to {r['ci_high']:.2f}", "verdict": _verdict(r)} for r in results]
    return pd.DataFrame(rows, columns=["hypothesis", "estimate", "CI", "verdict"])
```

## Complexity

O(number of hypotheses).

## Another way

Add a column with the test used and the size in business units, as the chapter does: the verdict is the summary, the other columns are what a reader checks.
