## Model answer

**1. The easy half.** Around a cycle the colours must alternate: every edge joins two different colours, so after each step the colour flips. After `L` steps the walk is back at the start, and the start must have flipped `L` times. If `L` is odd, the start would need the other colour than its own, which is impossible. If `L` is even, the start gets its own colour back, so red, blue, red, blue, ... closes up fine. A 5-cycle fails, a 6-cycle works.

**2. BFS layers.** If `u` is in layer `k`, a neighbour `v` is at most one step further: `dist(v) <= k + 1`. By the same argument from `v`'s side, `dist(u) <= dist(v) + 1`, so `dist(v) >= k - 1`. An edge therefore joins layers `k - 1`, `k` or `k + 1`, never layers that are 2 or more apart. Layer 2 and layer 5 cannot share an edge.

**3. Colour by parity.** An edge between neighbouring layers `k` and `k + 1` joins colours `k % 2` and `(k + 1) % 2`, which differ. So those edges are always fine. The only edges that can break the colouring are edges **inside one layer**.

**4. A bad edge gives an odd cycle.** Let `u` and `v` be in layer `k` with an edge between them. Their BFS-tree paths up towards `s` first meet at some vertex `a` in layer `j < k` (at worst at `s` itself). The path `a -> ... -> u` has `k - j` edges, so does `a -> ... -> v`, and the two share only `a`. With the edge `u - v` they form a cycle of `2(k - j) + 1` edges: always odd.

**5. Put it together.** If the graph has no odd cycle, step 4 says no edge lies inside a layer, and step 3 says the parity colouring then works: the graph is bipartite. Together with step 1, "bipartite" and "no odd cycle" are the same thing. The chapter's BFS colours exactly by layer parity (each new vertex gets the opposite colour of the vertex it was found from, which is one layer up). It reports a conflict only when an edge joins two vertices of the same colour. An edge joins layers at most one apart, and neighbouring layers have different colours, so the two vertices are in the same layer: step 4 gives an odd cycle, and the graph really is not bipartite. And if it finds no conflict, the colouring it built is a valid proof that the graph is bipartite. It cannot be wrong either way, and each connected piece is handled on its own.

**6. Use it.** A tree has no cycle at all, so no odd cycle: bipartite (colour by depth parity). A grid is bipartite: colour cell `(r, c)` with `(r + c) % 2`, every step changes `r + c` by one. A cycle of length 100 is bipartite (even). A cycle of length 101 is not (odd).

**7. Why not three colours?** With two colours, the colour of one vertex forces the colour of every vertex in its piece, so a single BFS either succeeds or finds a contradiction: there is nothing to try. With three colours, a neighbour of a red vertex may be blue **or** green; those choices branch, and a bad early choice may only show up much later. No trick like the BFS layers removes the branching: deciding whether three colours suffice is NP-complete, and no algorithm is known that does it in polynomial time for every graph. Two colours are special because "different from my neighbour" leaves exactly one option.

**Checklist: your answer should mention**
- [ ] colours alternate around a cycle, so an odd cycle cannot be two-coloured and an even one can
- [ ] an edge joins BFS layers that differ by at most one (`k - 1`, `k`, `k + 1`)
- [ ] colouring by layer parity makes every edge between neighbouring layers fine
- [ ] only an edge **inside one layer** can break the colouring
- [ ] such an edge closes a cycle of length `2(k - j) + 1` through the meeting point of the two tree paths: odd
- [ ] therefore "bipartite" is the same as "no odd cycle", and the BFS check is never wrong in either direction
- [ ] each connected piece is checked separately
- [ ] trees and grids are bipartite, an odd cycle is not
- [ ] with two colours every choice is forced; with three it branches (three-colouring is NP-complete)
