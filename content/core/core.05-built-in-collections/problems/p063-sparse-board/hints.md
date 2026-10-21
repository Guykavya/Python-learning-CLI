## Hint 1

A dict with `(r, c)` tuple keys stores only the non-zero cells. `get` is `cells.get((r, c), 0)`.

## Hint 2

Keep two more dicts: `row_sum[r]` and `col_sum[c]`. On `set`, subtract the cell's old value and
add the new one in both.

## Hint 3

When V is 0, delete the key (if it exists) so `count` is just `len(cells)`.
