# Explain: why do two colours suffice?

Chapter section 8 states a rule: **a graph is bipartite exactly when it has no cycle of odd length**, and the BFS two-colouring finds out which case you are in. The chapter shows the easy half (an odd cycle cannot be two-coloured). This problem asks you to explain the other half too, and why the BFS check can be trusted.

Write a short explanation (12 to 18 sentences) in `answer.md` that answers:

1. **The easy half.** Walk around a cycle of length 5 and try to colour it with two colours. Why must it fail? Why does a cycle of length 6 work? Say it for any odd and any even length.
2. **BFS layers.** Run a BFS from a vertex `s` of a connected graph. Layer `k` holds the vertices at distance `k` from `s`. Why can an edge never join layer 2 and layer 5? Which layers **can** an edge join?
3. **Colour by parity.** Colour every vertex of layer `k` with `k % 2`. Using your answer to 2, which edges are automatically fine, and which are the only edges that could break the colouring?
4. **A bad edge gives an odd cycle.** Suppose an edge joins two vertices `u` and `v` of the **same** layer `k`. Follow the BFS tree from `u` and from `v` back up towards `s` until the two paths first meet, at a vertex `a` in layer `j`. How long is the cycle `a -> ... -> u -> v -> ... -> a`? Why is that length odd?
5. **Put it together.** Why do 3 and 4 prove "no odd cycle means bipartite"? Why does that mean the BFS check in the chapter never says "not bipartite" for a bipartite graph, and never says "bipartite" for one that is not?
6. **Use it.** Without running anything: is every tree bipartite? A grid graph (cells joined up/down/left/right)? A cycle of length 100? A cycle of length 101? Give a one-line reason each.
7. **Why not three colours?** With two colours every choice after the first is **forced**. Why is that not true for three colours, and what does that mean for an algorithm that must decide whether three colours suffice?

Draw the small cases on paper first (a 5-cycle, a 6-cycle, a BFS of a 5-cycle with its layers). Then compare with the model answer and rate yourself.
