## Approach

History is never overwritten: a change **adds** a row and **closes** another. Facts keep pointing to the surrogate key that was current when they happened, and `lookup_key` finds that key by date.

## Code

```python
import pandas as pd

FOREVER = pd.Timestamp("2999-12-31")


def scd2_apply(dim, changes, as_of):
    as_of = pd.Timestamp(as_of)
    out = dim.copy()
    nxt = int(out["SurrogateKey"].max()) + 1 if len(out) else 1
    new_rows = []
    for cid, region in zip(changes["CustomerID"], changes["Region"]):
        cur = out[(out["CustomerID"] == cid) & out["IsCurrent"]]
        if len(cur) and cur["Region"].iloc[0] == region:
            continue
        if len(cur):
            out.loc[cur.index, ["ValidTo", "IsCurrent"]] = [as_of - pd.Timedelta(days=1), False]
        new_rows.append({"SurrogateKey": nxt, "CustomerID": cid, "Region": region, "ValidFrom": as_of, "ValidTo": FOREVER, "IsCurrent": True})
        nxt += 1
    if new_rows:
        out = pd.concat([out, pd.DataFrame(new_rows)], ignore_index=True)
    return out.sort_values("SurrogateKey").reset_index(drop=True)


def lookup_key(dim, customer_id, date):
    date = pd.Timestamp(date)
    v = dim[(dim["CustomerID"] == customer_id) & (dim["ValidFrom"] <= date) & (dim["ValidTo"] >= date)]
    if v.empty:
        raise ValueError("no version valid on that date")
    return int(v["SurrogateKey"].iloc[0])
```

## Complexity

O(changes x rows).

## Another way

Type 1 overwrites (no history, simple), type 3 keeps one previous value in a column (limited history), type 2 keeps everything: choose by how much history the reports need.
