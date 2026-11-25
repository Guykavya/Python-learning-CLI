## Approach

1. `df[df["a"] > 1]["b"] = 0` indexes twice. The first `[]` makes a temporary frame; the second sets a value in the temporary. `df` is unchanged (`[10, 20, 30]`), and pandas 3 records one `ChainedAssignmentError` warning, which `catch_warnings(record=True)` collected: `1 ChainedAssignmentError`.
2. `s = df["a"]` is lazily a copy: writing to `s` copies the data first. So `s` is `[99, 2, 3]` and `df["a"]` is still `[1, 2, 3]`.
3. `df.loc[df["a"] > 1, "b"] = 0` is one assignment on `df` itself: rows 1 and 2 get `b = 0`: `[10, 0, 0]`.
4. `y = x` is the same object under two names, so `y.iloc[0] = 9` is visible through `x`: `[9, 2, 3]`.
5. `z = x.copy()` is independent: only `z` changes (`[9, 50, 3]`); `x` keeps `[9, 2, 3]`.

## Code

The expected output is in `expected.txt`, produced by running the program (measured with pandas 3.1.1).

## Complexity

With Copy-on-Write, `df["a"]` and `copy()` are cheap: data is copied only when one of the two sides changes.

## Another way

To see the same rules in one picture, remember: *results of operations are copies; a second name is not*. And: when you want to change a table, write **one** `loc` on the table itself.
