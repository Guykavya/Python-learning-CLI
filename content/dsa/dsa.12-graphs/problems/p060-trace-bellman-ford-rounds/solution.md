## Approach

Relax the edges in their listed order, round after round, using every new value at once.

## Expected output

```text
round 1: [0, -1, 9, 9, 1, '-']
round 2: [0, -1, 2, 4, 1, '-']
round 3: [0, -1, 2, 1, 1, '-']
round 4: [0, -1, 2, 1, 1, '-']
no change: stop
[0, -1, 2, 1, 1, inf]
```


## Why

| round | changes, in edge order | after the round |
|---|---|---|
| 1 | `0->1`: 4, `0->2`: 9, `1->3`: 4 + 5 = 9, `0->4`: 1, `4->1`: 1 - 2 = -1 | `[0, -1, 9, 9, 1, -]` |
| 2 | `2->3`: 9 - 1 = 8, `1->2`: -1 + 3 = 2, `1->3`: -1 + 5 = 4 | `[0, -1, 2, 4, 1, -]` |
| 3 | `2->3`: 2 - 1 = 1 | `[0, -1, 2, 1, 1, -]` |
| 4 | none (`3->4` gives 3, not < 1; `4->1` gives -1, not < -1) | same, then `no change: stop` |

The best route to 3 is `0 -> 4 -> 1 -> 2 -> 3` (`1 - 2 + 3 - 1 = 1`), four edges. Because `1->2` and `2->3` come **before** `4->1` in the list, the route grows by about one edge per round: round 1 finds `0 4 1`, round 2 adds `1 2`, round 3 adds `2 3`. Round 4 finds nothing, so the rest cannot change either: every later round would see exactly the same distances. Vertex 5 stays infinite.

## Another way

Work out the true distances first (Dijkstra cannot be used because of the negative edges, but the graph is small): 1 is `-1` via 4, 2 is `2`, 3 is `1`, 4 is `1`. Then the rounds only have to "discover" these, one more edge of each best route per round in the worst case.
