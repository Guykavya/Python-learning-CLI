## Hint 1

Before the loop: write `adj` for every vertex (edges in the listed order) and count the in-degrees. For the first graph, which vertices have no edge pointing to them? Those are in the first `ready`, smallest first.

## Hint 2

Each `take` line removes one vertex from the **left** of `ready`, then lowers the in-degree of its targets in `adj` order, appending to the **right** each target that reaches 0. `adj[4]` is `[1, 0]` and both 1 and 0 reach 0 when 4 is taken, so `ready` becomes `[1, 0]` in that order.

## Hint 3

For the second graph: `indeg = [0, 2, 1, 1]` (vertex 1 has the edges from 0 and from 2). After taking 0, vertex 1 still waits for vertex 2, and 2 waits for 1. `ready` is empty after only one vertex, so `len(order) < n` and the last line says `cycle`.
