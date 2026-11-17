# DFS order (iterative)

The recursive DFS of p012 crashes with `RecursionError` on a chain of a few thousand vertices (chapter section 4, "The recursion-limit trap"). Real inputs have 100,000.

Write `dfs_order(n, edges, start)` **without recursion**, using a list as a stack. It must return **exactly the same order** as the recursive version of p012:

- Build the adjacency list in **edge-list order**: for an undirected edge `(u, v)` append `v` to `adj[u]` and `u` to `adj[v]`, in the order the edges are listed (problem p001; a self loop once).
- the recursive DFS visits `u`, then goes into the first unvisited neighbour of `u`, all the way down, before it tries the second one.

Two details decide whether a stack gives that order (chapter section 4, "DFS with a stack"). Think about them before you code:

1. In which order must the neighbours of `u` be pushed, so that the **first** neighbour is popped first?
2. A vertex can be pushed several times, by several neighbours. When do you mark it as visited: when it is pushed, or when it is popped? Which choice reproduces the recursive order?

## Example

```python
>>> dfs_order(5, [(0, 1), (0, 2), (1, 3), (3, 2), (1, 4)], 0)
[0, 1, 3, 2, 4]
>>> dfs_order(4, [(0, 1), (0, 2), (1, 2), (2, 3)], 0)
[0, 1, 2, 3]
```

In the second example `2` is a neighbour of `0`, but the recursive DFS reaches it first through `1`.

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges. `O(n + E)` time. The tests include a chain of 100,000 vertices.
