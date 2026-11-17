## Model answer

**1. A counterexample.** Edges `0 -> 1` (weight 1), `0 -> 2` (weight 3) and `2 -> 1` (weight -3). There is no cycle at all. The true distances from 0 are `[0, 0, 3]`: the best route to 1 is `0 -> 2 -> 1` with `3 - 3 = 0`. The `done`-set Dijkstra pops 0, gives 1 the distance 1 and 2 the distance 3, then pops 1 (distance 1, the smallest) and marks it **done**. When it pops 2 and finds the edge `2 -> 1` with `3 - 3 = 0`, vertex 1 is already done and is not touched. It returns `[0, 1, 3]`. Bellman-Ford returns `[0, 0, 3]`.

```python
edges = [(0, 1, 1), (0, 2, 3), (2, 1, -3)]
print(dijkstra_done_set(3, edges, 0), bellman_ford(3, edges, 0))   # [0, 1, 3] [0, 0, 3]
```

**2. The broken step.** The proof says: when `u` has the smallest tentative distance `d`, any other route to `u` must leave the settled region through some unsettled `x` with `dist[x] >= d`, and "the rest of that route adds weights that are never negative, so it cannot end below `d`". With the edge `2 -> 1` of weight -3, the route through `x = 2` starts at 3, which is more than 1, and the rest of the route **lowers** it to 0. The sentence "it cannot end below `d`" is false.

**3. Adding a constant does not help.** Add 3 to every weight: `0 -> 1` becomes 4, `0 -> 2` becomes 6, `2 -> 1` becomes 0. Now Dijkstra says the best route to 1 is the direct edge (4 against 6). But the direct route has 1 edge and pays the `+3` once, while `0 -> 2 -> 1` has 2 edges and pays it twice. The shift punishes routes with more edges, so the best route can change. Shortest routes are only kept when every route between the same two vertices is shifted by the same amount, and here the routes have different numbers of edges.

**4. Bellman-Ford.** It does not choose an order at all: it relaxes **every** edge, in `V - 1` rounds. After round `k`, every vertex whose best route has at most `k` edges is right, and this argument never uses the sign of the weights. It costs `O(V * E)`, much more than Dijkstra's `O((V + E) log V)`. A `V`-th round that still improves something reveals a negative cycle.

**5. The lazy version.** It is not "safe": it lets a vertex be popped again when its distance drops, so it often gives the right distances on graphs with negative edges and no negative cycle. But then a vertex is no longer final when it is popped, and it can be re-processed many times: on bad graphs the number of pops grows **exponentially**. With a negative cycle it never stops. Dijkstra's guarantee (each vertex settled once, `O((V + E) log V)`) holds only for non-negative weights; for negative edges use Bellman-Ford.

**Checklist: your answer should mention**
- [ ] a 3-vertex graph with one negative edge, no negative cycle, and two different results (true vs done-set Dijkstra)
- [ ] the vertex that was settled too early, and the edge that would have improved it
- [ ] the proof step "the rest of the route can only add" (non-negative weights) is what breaks
- [ ] adding a constant changes routes with different numbers of edges by different amounts
- [ ] Bellman-Ford: relax all edges `V - 1` times, `O(V * E)`, works with negative edges
- [ ] the lazy version may re-process vertices; its running time is no longer guaranteed (and it loops forever on a negative cycle)
