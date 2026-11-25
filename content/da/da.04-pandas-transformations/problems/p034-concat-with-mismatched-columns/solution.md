## Approach

1. `c = concat([a, b])` stacks 2 + 1 = 3 rows. The columns are the union in order of first appearance: `id`, `qty`
   (from `a`), `price` (from `b`). Shape `(3, 3)`.
2. Missing cells: rows 0 and 1 have no `price`, row 2 has no `qty`: 3 in total. `c["qty"].isna()` is
   `[False, False, True]`.
3. `join="inner"` keeps only the columns both tables have: `id`. Shape `(3, 1)`.
4. `concat([x, y], axis=1)` puts the two Series side by side, **aligned on the index**: the labels are the union `p, q, r`,
   so the shape is `(3, 2)`.
5. `x` has no `r`, so its column is `[1.0, 2.0, nan]` (a column with `NaN` becomes float); `y` has no `p`:
   `[nan, 10.0, 20.0]`.

## Code

The expected output is in `expected.txt`, produced by running the program with pandas 3.1.1.

## Complexity

`concat` copies every value once: O(total cells of the result).

## Another way

Before stacking files, compare their columns: `set(a.columns) ^ set(b.columns)` lists the names that only one side
has (`{'qty', 'price'}` here). An empty set means the stack will not create surprise `NaN` columns.
