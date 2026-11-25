## Approach

One pass over the relationships, reading the stored tables: the same checks you would do with pandas before a merge. The table of results is the model's health report.

## Code

```python
import pandas as pd


def check_relationships(m):
    rows = []
    for r in m.rels:
        many, one = m.t[r.many][r.mcol], m.t[r.one][r.ocol]
        rows.append({"relationship": f"{r.many}[{r.mcol}] -> {r.one}[{r.ocol}]", "one side unique": bool(one.is_unique),
                     "blank keys": int(many.isna().sum()), "orphan rows": int((~many.dropna().isin(one)).sum()),
                     "direction": "both" if r.both else "single", "active": bool(r.active)})
    return pd.DataFrame(rows)
```

## Complexity

O(rows of the fact tables).

## Another way

In Power BI, "Model view" shows the arrows and "Manage relationships" the cardinality; these checks find the data problems that the picture cannot show.
