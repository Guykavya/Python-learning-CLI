## Hint 1

The root is `go(0)` with an empty path. Its loop tries `i = 0, 1, 2`, which add the items 1, 2, 3. The child after adding item `nums[i]` is `go(i + 1)`.

## Hint 2

The child `go(1)` with path `[1]` runs completely (with all its own children) before the root tries `i = 1`. When a child returns, `path.pop()` removes its item again.

## Hint 3

The tree has one node per subset, so 8 lines of nodes, then the line with `len(answers)`.
