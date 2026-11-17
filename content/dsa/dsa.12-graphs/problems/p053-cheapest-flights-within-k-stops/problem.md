# Cheapest flights within K stops

There are `n` cities `0 .. n-1` and one-way `flights` given as `(from, to, price)`. Write `find_cheapest_price(n, flights, src, dst, k)`: the cheapest price from `src` to `dst` using **at most `k` stops**, or `-1` if no such route exists.

A **stop** is a city in between: a route with `k` stops uses `k + 1` flights. `src` to `dst` directly is 0 stops.

This is chapter section 12, "Paths with at most `k` edges, and the copy trap": Bellman-Ford with exactly `k + 1` rounds, where every round reads the distances of the **previous** round.

## Example

```python
>>> flights = [(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)]
>>> find_cheapest_price(4, flights, 0, 3, 1)
700
>>> find_cheapest_price(4, flights, 0, 3, 2)
400
```

With one stop, `0 -> 1 -> 3` costs 700. `0 -> 1 -> 2 -> 3` costs only 400 but has two stops, so it needs `k >= 2`.

## Constraints

- `1 <= n <= 100`, `0 <= len(flights) <= n * (n - 1)`, `1 <= price <= 10**4`, `0 <= k < n`, `src != dst`.
- Do not change `flights`.

## Think about

Why does plain Dijkstra give a wrong answer here? Why does updating the distance list **in place** during a round allow too many flights?
