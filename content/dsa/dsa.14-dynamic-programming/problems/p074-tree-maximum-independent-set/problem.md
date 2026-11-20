# Tree: maximum independent set size

A tree has `n` nodes `0 .. n-1` and is given as a list of `n - 1` edges `(a, b)`. An **independent set** is a set of nodes with no edge between any two of them. Write `max_independent_set(n, edges)` that returns the size of the **largest** independent set (chapter section 18, "Independent set and general trees").

## Example

```python
>>> max_independent_set(5, [(0, 1), (1, 2), (2, 3), (3, 4)])    # a path: nodes 0, 2, 4
3
>>> max_independent_set(5, [(2, 0), (2, 1), (2, 3), (2, 4)])    # a star: the four leaves
4
>>> max_independent_set(1, [])
1
>>> max_independent_set(2, [(1, 0)])
1
```

## Constraints

- `1 <= n <= 10**5`; the edges form one tree (connected, no cycles), in any order and direction.
- `O(n)` time.
- **The tree can be a path of 100,000 nodes.** A recursive walk then needs 100,000 nested calls, far beyond Python's recursion limit (1,000 by default). Your walk must be **iterative**. Raising the limit with `sys.setrecursionlimit` is not the lesson here: the large test sets the limit back to 1,000 after importing your file.

## Think about

The DP is the chapter's: `take(v) = 1 + sum of skip(child)`, `skip(v) = sum of max(take(child), skip(child))`. A node needs its children's values first: children before parents. If you list the nodes in **BFS order** from node 0, every parent comes before its children. What order do you get if you walk that list **backwards**?
