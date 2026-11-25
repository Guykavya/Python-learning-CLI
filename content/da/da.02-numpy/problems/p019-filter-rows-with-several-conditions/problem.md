# Filter rows with several conditions

Chapter sections 8.1 to 8.3. An orders table is a 2-D array, one row per order, for example the columns
`[order_id, amount, refunded]` where `refunded` is 1 or 0. Write two functions:

- `select_rows(table, col, lo, hi, exclude=None)`: the rows whose value in column `col` is between `lo` and `hi`
  (**both included**). If `exclude` is a column index, also drop the rows whose value in that column is **not 0**
  (a flag column such as `refunded`).
- `outside_rows(table, col, lo, hi)`: the rows whose value in column `col` is **below `lo` or above `hi`**.

Both keep the original row order, keep all the columns, and return an array of shape `(0, ncols)` when no row matches.
The input is not changed. Use masks with `&`, `|` and `~`: and put each comparison in **brackets** (Ch. 8.2).

## Example

```python
orders = np.array([
    [101,  50, 0],
    [102, 250, 1],
    [103, 400, 0],
    [104, 999, 0],
    [105, 120, 0],
])
select_rows(orders, 1, 100, 400).tolist()
# [[102, 250, 1], [103, 400, 0], [105, 120, 0]]
select_rows(orders, 1, 100, 400, exclude=2).tolist()
# [[103, 400, 0], [105, 120, 0]]
outside_rows(orders, 1, 100, 400).tolist()
# [[101, 50, 0], [104, 999, 0]]
```
