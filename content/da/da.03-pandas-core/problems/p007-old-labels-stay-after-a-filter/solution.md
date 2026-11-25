## Approach

The filter keeps rows with labels 1, 2, 3 (values 6, 7, 8), so the index stays `[1, 2, 3]` and the shape is `(3, 2)`. `kept.loc[0, "n"]` asks for a label that is gone: `KeyError`, caught and printed by class name. The first kept row by position (`iloc[0]`) is the one labelled 1, value 6; `loc[2, "n"]` is label 2, value 7. After `reset_index(drop=True)` the labels are `0, 1, 2` again, so `loc[0, "n"]` is 6. Without `drop=True`, the old labels become a new first column called `index`.

## Code

The expected output is in `expected.txt`, produced by running the program.

## Complexity

A filter is O(n); `reset_index` is O(n) too.

## Another way

Print `kept.index.tolist()` after every filter while you learn. Use `reset_index(drop=True)` only when the old labels carry no meaning.
