# `isin`, `between` and `.str.contains`

Chapter section 8.2. Three helpers make filters readable: `isin` (is the value one of a list?), `between` (a range, **both
ends included**) and `.str.contains` (does the text contain a word?).

Write `filter_products(df, categories, lo, hi, word)` returning the rows where:

- `category` is one of `categories`;
- `price` is between `lo` and `hi`, both included;
- `name` contains `word`, ignoring upper and lower case. A missing name does **not** match (and must not crash).
  Treat `word` as plain text, not as a pattern: `"c++"` or `"(x)"` must work.

Keep the original index labels and all columns. The input is not changed.

## Example

```python
df = pd.DataFrame({
    "name": ["Green Tea", "tea bags", None, "Coffee", "TEA cup"],
    "category": ["food", "food", "food", "food", "home"],
    "price": [120.0, 80.0, 90.0, 200.0, 150.0],
})
filter_products(df, ["food"], 80, 200, "tea").index.tolist()    # [0, 1]
```
