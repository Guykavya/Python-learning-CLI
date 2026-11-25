## Approach

`keep="last"` trusts the current row order, so create the order you want first: sort ascending by time and, for equal times, by `row_id`; the last row of every customer is then the newest, with the larger `row_id` winning ties. After `drop_duplicates` on `customer`, sort by customer for a readable result and reset the index. The number removed is rows in minus rows out. No loop is needed, and `sort_values` returns a new frame, so the input stays unchanged.

## Code

```python
def latest_per_customer(df):
    ordered = df.sort_values(["ts", "row_id"])
    latest = (ordered.drop_duplicates(subset="customer", keep="last")
                     .sort_values("customer").reset_index(drop=True))
    return latest, len(df) - len(latest)
```

## Complexity

O(n log n) for the sorts, O(n) for the duplicate step.

## Another way

`df.sort_values(["ts", "row_id"]).groupby("customer").tail(1)` does the same (da.04 teaches `groupby`), and `idxmax` on a combined key works when you only need one winner. The sorted version is the one that makes the tie rule visible: it is just the columns of the sort.
