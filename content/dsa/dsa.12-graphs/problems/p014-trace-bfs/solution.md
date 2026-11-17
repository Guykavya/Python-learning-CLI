## Approach

Write the seven adjacency lists in edge-list order, then simulate the queue. A neighbour is added once, the first time it is seen, with the distance of the vertex that found it plus one.

## Expected output

```text
pop 0: queue=[2, 1] dist={0: 0, 2: 1, 1: 1}
pop 2: queue=[1, 4, 3] dist={0: 0, 2: 1, 1: 1, 4: 2, 3: 2}
pop 1: queue=[4, 3] dist={0: 0, 2: 1, 1: 1, 4: 2, 3: 2}
pop 4: queue=[3, 5] dist={0: 0, 2: 1, 1: 1, 4: 2, 3: 2, 5: 3}
pop 3: queue=[5] dist={0: 0, 2: 1, 1: 1, 4: 2, 3: 2, 5: 3}
pop 5: queue=[6] dist={0: 0, 2: 1, 1: 1, 4: 2, 3: 2, 5: 3, 6: 4}
pop 6: queue=[] dist={0: 0, 2: 1, 1: 1, 4: 2, 3: 2, 5: 3, 6: 4}
```

## Why

| pop | `adj[u]` | new vertices (distance) | queue after |
|---|---|---|---|
| 0 | 2, 1 | 2 (1), 1 (1) | `[2, 1]` |
| 2 | 0, 4, 3 | 4 (2), 3 (2) | `[1, 4, 3]` |
| 1 | 0, 3 | none (3 is already known) | `[4, 3]` |
| 4 | 2, 5 | 5 (3) | `[3, 5]` |
| 3 | 1, 2, 5 | none | `[5]` |
| 5 | 4, 3, 6 | 6 (4) | `[6]` |
| 6 | 5 | none | `[]` |

`3` was discovered by `2`, because `2` left the queue before `1`; both are at distance 1, so `dist[3]` is 2 either way. `5` is found by `4` first, also at distance 2, so it gets 3; `3` would also give 3. BFS adds vertices in waves, so the distances in `dist`'s insertion order never go down: 0, 1, 1, 2, 2, 3, 4.

## Another way

Draw the BFS tree (each vertex with an arrow to the vertex that discovered it): `2 <- 0 -> 1`, `4 <- 2 -> 3`, `5 <- 4`, `6 <- 5`. The depth of each vertex in that tree is its `dist`.
