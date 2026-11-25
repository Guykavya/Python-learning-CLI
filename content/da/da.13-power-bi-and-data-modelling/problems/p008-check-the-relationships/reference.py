import pandas as pd


def check_relationships(m):
    rows = []
    for r in m.rels:
        many, one = m.t[r.many][r.mcol], m.t[r.one][r.ocol]
        rows.append({"relationship": f"{r.many}[{r.mcol}] -> {r.one}[{r.ocol}]", "one side unique": bool(one.is_unique),
                     "blank keys": int(many.isna().sum()), "orphan rows": int((~many.dropna().isin(one)).sum()),
                     "direction": "both" if r.both else "single", "active": bool(r.active)})
    return pd.DataFrame(rows)
