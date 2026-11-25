## Approach

Three disjoint groups of lines add up to the control total: lines in the grid, lines lost to the first cause, lines lost to the second. Putting the causes in a fixed priority order makes the bridge exact and unambiguous: every line is in exactly one group, so nothing is counted twice and `unexplained` is zero when the causes are complete.

## Code

```python
import pandas as pd


def bridge(df, regions, valid_codes):
    units = df["units"].map(float)
    rev = units * df["unit_price"] * (1 - df["discount"])
    code_bad = ~df["product_code"].map(lambda c: str(c).upper() in valid_codes)
    ok_regions = {r.lower() for r in regions}
    region_bad = ~df["region"].map(lambda r: str(r).lower() in ok_regions)
    control = float(rev.sum())
    grid = float(rev[~code_bad & ~region_bad].sum())
    causes = {"product code not found": float(rev[code_bad].sum()),
              "region not matched": float(rev[~code_bad & region_bad].sum())}
    gap = control - grid
    return {"control_total": control, "grid_total": grid, "gap": gap, "causes": causes,
            "unexplained": gap - sum(causes.values())}
```

## Complexity

O(n).

## Another way

Report the bridge as a small table (step, amount, running total) as the chapter does: a manager reads it from top to bottom and sees the grid total climb to the control total, one cause at a time.
