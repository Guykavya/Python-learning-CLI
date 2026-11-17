## Hint 1

A non-root vertex `u` cuts the graph when some child subtree has no back edge that reaches **above** `u`: everything in that subtree reaches the rest only through `u`. Reaching `u` itself is not enough, because `u` is the vertex being removed. Which comparison of `low[c]` and `tin[u]` says that?

## Hint 2

For the root, `low[c] >= tin[root]` is always true (nothing is above the root), so the normal rule would mark every root. The root cuts the graph only if it has two or more DFS children: different child subtrees of the root are never joined by an edge (otherwise the DFS would have entered the second one from the first).

## Hint 3

Same iterative DFS as for bridges, with frames `(u, edge you came by, iterator)`. When a child `c` finishes and its parent `p` is on top of the stack: `low[p] = min(low[p], low[c])`; if `p` is not the root and `low[c] >= tin[p]`, mark `p`. Count the children of the root as you push them; after the DFS of that tree, mark the root if the count is at least 2.
