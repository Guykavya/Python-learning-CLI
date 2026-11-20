## Hint 1

`FenwickTree(n_or_list)`: `isinstance(n_or_list, int)` means a size; otherwise build from the list with the `O(n)` method of p014 (push each cell into its parent).

## Hint 2

`SegmentTree` is the iterative tree of p006: two accumulators `resl` / `resr` so that string concatenation comes out in order. `SparseTable` is p023 with `f` instead of `min`.

## Hint 3

Reuse your own code from p006, p014 and p023; put the three classes in one file. Run the shared tests: a failure names the structure, the operation and the step.
