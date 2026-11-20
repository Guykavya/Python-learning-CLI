# Largest component

A social network wants to show its biggest group of people who are all linked through friends of friends. That is the **largest connected component** of the friendship graph.

Write `largest_component(n, edges)` for an undirected graph with vertices `0 .. n-1`. It returns the vertices of the largest component as a **sorted** list.

If several components have the same largest size, return the one that contains the **smallest vertex number** (that is the one your outer loop finds first if it goes from `0` up).

## Example

```python
>>> largest_component(7, [(0, 1), (2, 3), (3, 4), (5, 6), (6, 2)])
[2, 3, 4, 5, 6]
>>> largest_component(4, [(2, 3), (0, 1)])
[0, 1]
>>> largest_component(3, [])
[0]
```

In the second example `{0, 1}` and `{2, 3}` both have size 2; `{0, 1}` contains the smaller vertex `0`.

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges. `O(n + E)` plus sorting the answer. The tests include a chain of 100,000 vertices.
