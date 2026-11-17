## Hint 1

The grid, with coordinates:

```text
     0 1 2 3
  0  a a b .
  1  a . b a
  2  a a a b
  3  b . a b
```

From `(0, 0)`: up and left are outside; down `(1, 0)` is `a`, right `(0, 1)` is `a`. Both are painted and queued, in that order (down comes before right in the code).

## Hint 2

The queue is first in, first out. After `(1, 0)` adds `(2, 0)`, the next cell to visit is still `(0, 1)`, which was queued earlier. The region goes down the left column, then right along row 2, then down to `(3, 2)`. Check every neighbour of `(2, 2)`: which of them are `a`?
