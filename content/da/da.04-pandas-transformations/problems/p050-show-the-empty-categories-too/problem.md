# Show the empty categories too

Chapter sections 10.3 and 10.4. A size report must list **every** size the shop sells, including sizes nobody
ordered (a 0 is information: "nobody bought XL"). In pandas 3, `groupby` on a categorical column defaults to
`observed=True`, so categories with no rows simply vanish, without a warning.

Write `orders_per_size(df)`:

- `df` has one row per order line and a column `size` that is already an ordered categorical (the categories are the
  sizes the shop sells, in order); a few lines have a missing size;
- return a frame with the columns `size` and `orders`: one row per **category**, in category order, with the number
  of lines of that size (0 for an unused size). Lines with a missing size are not counted. Fresh index;
- do not change the input.

## Example

```python
import pandas as pd

sizes = pd.CategoricalDtype(["S", "M", "L"], ordered=True)
df = pd.DataFrame({"order_id": [1, 2, 3], "size": pd.Series(["M", "S", "M"], dtype=sizes)})
out = orders_per_size(df)
print(out["size"].astype(str).tolist(), out["orders"].tolist())
```
```text
['S', 'M', 'L'] [1, 2, 0]
```
