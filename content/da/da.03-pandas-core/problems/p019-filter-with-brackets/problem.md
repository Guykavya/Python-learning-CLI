# Filter with brackets

Chapter section 8.1 to 8.3. Combine conditions with `&` (and), `|` (or) and `~` (not). These operators bind more tightly
than comparisons, so each comparison needs **its own parentheses**: `df.a > 1 & df.b < 2` is an error.

Write `big_orders(df, city, min_amount)` returning the rows that are:

- not cancelled (`status` is not `"cancelled"`), **and**
- either from `city` with `amount >= min_amount`, **or** flagged `rush` (a boolean column).

The result keeps the original index labels and all columns, and the input is not changed.

## Example

```python
df = pd.DataFrame({
    "city": ["Pune", "Pune", "Agra", "Agra"],
    "amount": [500, 100, 90, 800],
    "status": ["paid", "paid", "paid", "cancelled"],
    "rush": [False, False, True, True],
})
big_orders(df, "Pune", 400).index.tolist()    # [0, 2]
```

Row 0 is a big Pune order, row 1 is too small, row 2 is a rush order, row 3 is cancelled (even though it is a rush).
