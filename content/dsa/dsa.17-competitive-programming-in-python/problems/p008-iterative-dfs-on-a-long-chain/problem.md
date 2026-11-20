# Iterative DFS on a long chain

A tree has `n` vertices numbered `1..n`, rooted at vertex `1`. The depth of the root is `0`, the depth of a child is the depth of its parent plus one.

Print two numbers: the **maximum depth** and the **sum of the depths of all vertices**.

## Input

The first line holds `n` (`1 <= n <= 2 * 10**5`). Then `n - 1` lines follow, each holding an edge `u v` (undirected, in any order and orientation).

## Output

One line: `max_depth sum_of_depths`.

## Example

```text
5
1 2
2 3
1 4
4 5
```
```text
2 6
```

Depths: vertex 1: 0; vertices 2 and 4: 1; vertices 3 and 5: 2. The maximum is 2, the sum is 6.

## The catch

If the tree is a **path** of `2 * 10**5` vertices, a recursive DFS goes `2 * 10**5` calls deep. CPython's default recursion limit is 1000, so a plain recursive solution fails with `RecursionError`. Use an explicit stack (or a queue), as in chapter section 8: never rely on `setrecursionlimit` for this.
