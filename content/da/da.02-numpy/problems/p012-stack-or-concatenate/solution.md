## Approach

Sort the calls into two families.

- **Joining an existing axis** adds lengths: `concatenate([u, v])` → `(6,)`; `hstack` of 1-D vectors is the same. For `P` and `Q`, axis 0 gives `(4, 3)` (also `vstack`) and axis 1 gives `(2, 6)` (also `hstack` and `column_stack`).
- **Stacking** inserts a new axis of length 2 (two arrays) at the given position: on `(3,)` that is `(2, 3)` or `(3, 2)`; on `(2, 3)` it is `(2, 2, 3)` at position 0 or 1 and `(2, 3, 2)` at position 2.
- `vstack` of 1-D vectors treats each as a row: `(2, 3)`, the same as `stack`. `column_stack` treats each as a column: `(3, 2)` with rows `[1, 4]`, `[2, 5]`, `[3, 6]`, the same as `stack(axis=1)`.
- `np.stack([P, Q], axis=1)[0]` takes row 0 from both: `[[0, 1, 2], [10, 11, 12]]`.

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

Every join copies all the data into a new array: O(total size). Joining in a loop (`result = np.concatenate([result, piece])` again and again) is therefore O(n²); collect pieces in a list and join once.

## Another way

`np.stack([P, Q], axis=1)` and `np.stack([P, Q])` have the same shape here only because `P` has 2 rows and there are 2 arrays. Try three arrays to see the difference: `(3, 2, 3)` vs `(2, 3, 3)`.
