# Change values with `loc`

Chapter section 9. To change some cells of a table, use **one** `.loc[rows, column] = value`. It names the rows (a mask), the
column and the new value in a single step.

Write `apply_discount(df, category, pct)` that returns a **new** frame in which the `price` of every row whose
`category` equals `category` is reduced by `pct` percent (`price * (1 - pct / 100)`). Other rows and other columns stay as
they are. The input frame is **not** changed.

## Example

```python
df = pd.DataFrame({"item": ["tea", "pen", "mug"], "category": ["food", "office", "home"], "price": [100.0, 20.0, 50.0]})
apply_discount(df, "food", 10)["price"].tolist()    # [90.0, 20.0, 50.0]
df["price"].tolist()                                 # [100.0, 20.0, 50.0]   unchanged
```
