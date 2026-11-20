## Hint 1

The adjacency lists are `adj[0] = [2, 1]`, `adj[1] = [0, 3]`, `adj[2] = [0, 4, 3]`, `adj[3] = [1, 2, 5]`, `adj[4] = [2, 5]`, `adj[5] = [4, 3, 6]`, `adj[6] = [5]`. Check one of them against the edge list before you go on.

## Hint 2

The first pop takes `0`; both `2` and `1` are new, so they get distance 1 and the queue becomes `[2, 1]`. The second pop takes `2` (the front): `0` is known, `4` and `3` are new. Continue the same way; when a vertex has no new neighbours, its line shows a shorter queue and the same `dist`.
