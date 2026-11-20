# Min cost to connect all points

`points` is a list of `(x, y)` points with integer coordinates. Joining two points costs their **Manhattan distance** `|x1 - x2| + |y1 - y2|`. Write `min_cost_connect_points(points)`: the smallest total cost to join all points so that every point can reach every other (a minimum spanning tree of the **complete** graph).

Every pair of points is an edge: with `n` points that is `n (n - 1) / 2` edges, about half a million for `n = 1000`. Chapter section 15 ("Dense graphs: Prim without a heap") solves this in `O(n^2)` with `O(n)` memory: keep `best[v]`, the cheapest way to join `v` to the tree so far, and pick the smallest by scanning.

## Example

```python
>>> min_cost_connect_points([(0, 0), (2, 2), (3, 10), (5, 2), (7, 0)])
20
>>> min_cost_connect_points([(3, 12), (-2, 5), (-4, 1)])
18
>>> min_cost_connect_points([(0, 0)])
0
```

## Constraints

- `1 <= n <= 1000`, `-10**6 <= x, y <= 10**6`, all points different. Return an `int`.

## Think about

Why is Kruskal on all pairs heavier here (time and memory)? Why is "always join the nearest unjoined point to the last point" not the same as Prim?
