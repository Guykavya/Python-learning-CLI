## Hint 1

The adjacency lists, in edge order, are: `0: (1,7) (2,2)`, `1: (0,7) (2,3) (3,1)`, `2: (0,2) (1,3) (3,8) (4,9)`, `3: (1,1) (2,8) (4,2)`, `4: (3,2) (2,9)`. The first pop is `(0, 0)`: it pushes `(7, 1)` and `(2, 2)`. Which pair comes out next?

## Hint 2

When `(2, 2)` is popped, vertex 1 can be reached for `2 + 3 = 5`, better than 7: `dist[1]` becomes 5 and `(5, 1)` is pushed, but `(7, 1)` stays in the heap. Later, when `(7, 1)` comes out, `7 > dist[1] = 5`: that is a stale pop. Count how many pairs each vertex gets.
