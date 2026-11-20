## Approach

Sort stably, then follow the parent pointers by hand for each edge.

## Expected output

```text
sorted: [(3, 5, 1), (1, 2, 2), (3, 4, 2), (4, 5, 2), (2, 3, 3), (0, 1, 4), (0, 2, 4), (1, 3, 5)]
take 3-5 (1): total 1
take 1-2 (2): total 3
take 3-4 (2): total 5
skip 4-5 (2): same group
take 2-3 (3): total 8
take 0-1 (4): total 12
tree complete
12
```


## Why

| edge | find(u) | find(v) | action | parent after |
|---|---|---|---|---|
| `3-5 (1)` | 3 | 5 | take, total 1 | `[0, 1, 2, 5, 4, 5]` |
| `1-2 (2)` | 1 | 2 | take, total 3 | `[0, 2, 2, 5, 4, 5]` |
| `3-4 (2)` | 5 (3 -> 5) | 4 | take, total 5 | `[0, 2, 2, 5, 4, 4]` |
| `4-5 (2)` | 4 | 4 (5 -> 4) | skip | |
| `2-3 (3)` | 2 | 4 (3 -> 5 -> 4) | take, total 8 | `[0, 2, 4, 5, 4, 4]` |
| `0-1 (4)` | 0 | 4 (1 -> 2 -> 4) | take, total 12, 5 edges: complete | `[4, 2, 4, 5, 4, 4]` |

Vertex 4 is the root of the whole tree. The edges `(0, 2, 4)` and `(1, 3, 5)` were never looked at: once a tree has `n - 1` edges, every other edge joins two vertices of the same group and would be skipped anyway. With `(4, 5, 2)` first, `4-5` would be taken and `3-4` skipped instead: a different tree, the same total 12 (both edges weigh 2).

## Another way

Check the total without Union-Find: the tree must connect 0 .. 5 with 5 edges. The cheapest edges 1, 2, 2 (the triangle 3-4-5 has three edges, so one of its 2s must go), then 3 for `2-3` and the cheapest edge to vertex 0, which is 4: `1 + 2 + 2 + 3 + 4 = 12`.
