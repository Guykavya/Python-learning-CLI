# Integers with gaps

Chapter section 10.2. A column of whole numbers with a missing value becomes `float64` (`NaN` is a float), so `3`
turns into `3.0`. The **nullable** dtype `Int64` keeps the integers and shows the gap as `<NA>`.

Write `to_nullable_ints(df, cols)` that returns a copy of `df` in which each column named in `cols` has the dtype `Int64`:

- values such as `3.0` become `3`; missing values stay missing (`<NA>`);
- if a column holds a value that is **not** a whole number (like `2.5`), raise `ValueError` whose message names that column;
- other columns, the index and the input frame are not changed.

## Example

```python
df = pd.DataFrame({"qty": [1.0, None, 3.0], "price": [1.5, 2.5, 3.5]})
out = to_nullable_ints(df, ["qty"])
out["qty"].tolist()       # [1, <NA>, 3]
str(out["qty"].dtype)     # 'Int64'
out["price"].dtype        # float64, untouched
to_nullable_ints(pd.DataFrame({"n": [1.0, 2.5]}), ["n"])   # ValueError: column 'n' has non-integer values
```
