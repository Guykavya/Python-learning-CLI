## The printed lines

```text
start: ready=[3, 4] indeg=[1, 2, 2, 0, 0, 2]
take 3: ready=[4] indeg=[1, 1, 2, 0, 0, 2]
take 4: ready=[1, 0] indeg=[0, 0, 2, 0, 0, 2]
take 1: ready=[0] indeg=[0, 0, 1, 0, 0, 2]
take 0: ready=[2] indeg=[0, 0, 0, 0, 0, 1]
take 2: ready=[5] indeg=[0, 0, 0, 0, 0, 0]
take 5: ready=[] indeg=[0, 0, 0, 0, 0, 0]
order: [3, 4, 1, 0, 2, 5]
start: ready=[0] indeg=[0, 2, 1, 1]
take 0: ready=[] indeg=[0, 1, 1, 1]
order: cycle
```

## Walkthrough

**First graph.** The adjacency lists are `adj[3] = [1]`, `adj[4] = [1, 0]`, `adj[1] = [2]`, `adj[0] = [2, 5]`, `adj[2] = [5]`, and `adj[5] = []`. Edges end at 1 twice (from 3 and 4), at 0 once, at 2 twice, at 5 twice, so `indeg = [1, 2, 2, 0, 0, 2]` and `ready = [3, 4]`.

- Take 3: its only edge lowers vertex 1 from 2 to 1. Nothing is ready.
- Take 4: `adj[4] = [1, 0]`. Vertex 1 drops to 0 and is appended, then vertex 0 drops to 0 and is appended: `ready = [1, 0]`.
- Take 1: vertex 2 drops from 2 to 1.
- Take 0: vertex 2 drops to 0 (appended), vertex 5 drops from 2 to 1.
- Take 2: vertex 5 drops to 0 (appended).
- Take 5: no edges. `ready` is empty and all 6 vertices are in the order.

**Second graph.** `adj[0] = [1]`, `adj[1] = [2]`, `adj[2] = [1, 3]`. In-degrees: vertex 1 gets the edges from 0 and 2, vertex 2 from 1, vertex 3 from 2: `[0, 2, 1, 1]`. Only 0 is ready. Taking 0 lowers vertex 1 to 1. Now nothing is ready, the loop stops after one vertex, and `len(order) = 1 < 4` prints `cycle`.

## Answers to "After you answer"

1. Both reach 0 in the same step, and the loop handles `adj[4]` from left to right: 1 is appended first, so it is taken first.
2. Vertices 1, 2 and 3, with in-degrees 1, 1 and 1. Vertex 1 waits for vertex 2, and vertex 2 waits for vertex 1: each can only be lowered by taking the other, so neither is ever taken.
3. Vertex 3 waits for vertex 2, which is stuck on the cycle. Kahn reports a cycle by leaving out the vertices **on** it and everything **behind** it.

## Complexity

Every vertex is taken once and every edge lowers one in-degree once: `O(V + E)`.

## Another way to check your answer

Without the prints: a valid topological order puts every edge's start before its end. Check your `order` line against all 7 edges of the first graph. Many orders are valid (`[4, 0, 3, 1, 2, 5]` too), but this program, with its queue, produces exactly one of them.
