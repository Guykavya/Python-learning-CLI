## Hint 1

Go line by line through the script and name each step as a method: a new column (`assign`), a row filter (`query` or `loc`), de-duplication, sorting, renumbering, column selection. Which of them needs the frame **as built so far**, and what does `assign(name=lambda d: ...)` give you for that?

## Hint 2

```text
return (
    df
    .assign(city=lambda d: d["city"].str.strip().str.title())     # t1
    .query("qty > 0")                                             # t2
    .drop_duplicates(subset="order_id", keep="last")              # t3
    .assign(revenue=lambda d: ... d["qty"] ... d["discount"].fillna(0) ...)   # t4
    .query("paid")                                                # t5  (paid is already True/False)
    .sort_values("revenue", ascending=False)                      # t6
    .reset_index(drop=True)                                       # t7
    .loc[:, ["order_id", "city", "revenue"]]                      # the last line of the script
)
```
`df.assign` returns a new frame, so the caller's table stays unchanged without `copy()`.
