## Hint 1

The root is `go(1)` with an empty path. Its loop tries `x = 1, 2, 3, 4`. The child after choosing `x` is `go(x + 1)`.

## Hint 2

The child with path `[1]` tries `x = 2, 3, 4`; each grandchild has a full path, prints its line and returns. Note the `start` of each grandchild: one more than its last item.

## Hint 3

The child with path `[4]` is `go(5)`: its loop `range(5, 5)` is empty, so it prints a line and returns without any answer.
