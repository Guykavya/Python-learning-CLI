## Approach

Each temporary variable is the output of one step and the input of the next, which is exactly what a method chain says without names. The steps map one to one: the first `assign` replaces `t1["city"] = ...` (and does the copying for you), `query("qty > 0")` is the first filter, `drop_duplicates` and `sort_values` and `reset_index` keep their names, the second `assign` uses a `lambda d:` so it sees the frame after the filters (not the original `df`: using `df["qty"]` inside the chain would refer to the *unfiltered* column and misalign), and `.loc[:, [...]]` or plain `[[...]]` picks the columns. Wrap the whole chain in brackets so each step has its own line.

## Code

```python
def clean_orders(df):
    return (
        df
        .assign(city=lambda d: d["city"].str.strip().str.title())
        .query("qty > 0")
        .drop_duplicates(subset="order_id", keep="last")
        .assign(revenue=lambda d: d["qty"] * d["unit_price"] * (1 - d["discount"].fillna(0)))
        .query("paid")
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
        .loc[:, ["order_id", "city", "revenue"]]
    )
```

## Complexity

The same work as the script: O(n log n) for the sort, O(n) for everything else. A chain does not make code faster; it makes it **readable** and removes the chance of using `t3` where `t4` was meant.

## Another way

For a step that has no method, write a small function and use `pipe`: `.pipe(drop_returns, min_qty=1)`. To debug a chain, stop it after any step (comment out the rest) or insert `.pipe(lambda d: (print(len(d)), d)[1])` to print the row count. If a chain grows beyond about eight steps, cut it into two named pieces (chapter 17.1).
