# K closest points to the origin

Write `k_closest(points, k)`. `points` is a list of tuples `(x, y)` with integer coordinates. Return a **list** of the `k` points that are closest to the origin `(0, 0)`.

The order of the result is fixed:

1. by distance from the origin, **nearest first**;
2. points at the **same distance** by `(x, y)` in the usual tuple order: smaller `x` first, and for the same `x` the smaller `y` first.

Rules:

- Compare **squared** distances, `x*x + y*y`. Do not use `sqrt`: with big coordinates the float result is not exact, and two points at different distances can look equal.
- `k <= 0` gives `[]`. If `k` is at least the number of points, return all points in that order.
- A point can appear more than once in the input; every copy counts.
- Return the points themselves (tuples). Do not change `points`.

## Example

```python
>>> k_closest([(3, 3), (5, -1), (-2, 4), (0, 1), (-1, -1)], 2)
[(0, 1), (-1, -1)]
>>> k_closest([(1, 0), (0, 1), (-1, 0), (0, -1)], 2)    # all at distance 1: (x, y) order decides
[(-1, 0), (0, -1)]
>>> k_closest([(2, 2)], 3)
[(2, 2)]
```

The squared distances in the first example are 18, 26, 20, 1 and 2: the two smallest belong to `(0, 1)` and `(-1, -1)`.

## Constraints

- `0 <= len(points) <= 10**5`, `-10**9 <= x, y <= 10**9`.
- A heap of size `k` takes `O(n log k)` time and `O(k)` extra memory. Sorting all the points (`O(n log n)`) also passes the tests, but then you have not practised the heap.

## Think about

You want the `k` **smallest** distances. The chapter says: for the K smallest keep a **max**-heap of size K. Why is the root of that heap the point to throw away? And how do you give `heapq` (a min-heap) a max-heap? (Hint: the key `(-d, ...)`.)
