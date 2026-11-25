## Approach

1. `u = s.unstack()` moves the innermost level (`channel`) into the columns. Rows are the stores, so the shape is
   `(3, 2)`, `index.names` is `['store']`, columns `['online', 'store']`.
2. `u0 = s.unstack(0)` moves level 0 (`store`) up instead: rows `online, store` named `channel`, columns
   `S1, S2, S3`: `(2, 3)`.
3. `u.loc["S2"]` is S2's row: online 2, store 4, so `[2, 4]`.
4. `u0.loc["store"]` is the row of the channel `store`: S1 7, S2 4, S3 1, so `[7, 4, 1]`.
5. `u.stack()` puts the columns back as the inner level: 6 values, levels `['store', 'channel']`, in row order:
   `[5, 7, 2, 4, 9, 1]`, the original Series.
6. After dropping `("S3", "store")`, the table still has a `store` column (S1 and S2 have one), so S3's cell there is
   missing: `1`.

## Code

The expected output is in `expected.txt`, produced by running the program with pandas 3.1.1.

## Complexity

Both moves are reshapes of n values: O(n) plus sorting the labels.

## Another way

`unstack("channel")` and `unstack("store")` name the level instead of numbering it, which reads better and survives a
change in the level order. `s.reset_index().pivot(index="store", columns="channel", values=0)` is the same as `u`
through `pivot`.
