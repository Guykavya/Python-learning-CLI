# Connected components count

An undirected graph falls apart into **connected components**: groups in which everyone can reach everyone (chapter section 5). A vertex with no edges is a component on its own.

Write `count_components(n, edges)` for an undirected graph with vertices `0 .. n-1`. It returns the number of connected components.

## Example

```python
>>> count_components(5, [(0, 1), (1, 2), (3, 4)])
2
>>> count_components(5, [(0, 1)])
4
>>> count_components(3, [(0, 1), (1, 2), (2, 0)])
1
```

In the second example the components are `{0, 1}`, `{2}`, `{3}` and `{4}`.

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges, self loops and parallel edges possible. `O(n + E)` time. The tests include a chain of 100,000 vertices.
