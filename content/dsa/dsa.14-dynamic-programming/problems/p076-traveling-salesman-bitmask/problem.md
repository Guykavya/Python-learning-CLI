# Traveling salesman (bitmask)

A delivery driver starts at depot `0`, must visit every one of the `n` places exactly once, and comes back to the depot. `dist[a][b]` is the driving time from `a` to `b`. Roads may be **one-way**, so `dist[a][b]` and `dist[b][a]` can differ.

Write `shortest_tour(dist)` that returns `(length, order)`:

- `length` is the shortest total time of such a round trip, including the drive back to 0;
- `order` is the visiting order: a list that starts with `0` and contains every place exactly once (the return to 0 is **not** repeated at the end).

Use the bitmask DP of chapter section 19, and rebuild the order from it.

## Example

```python
>>> shortest_tour([[0, 10, 15, 20],
...                [10, 0, 35, 25],
...                [15, 35, 0, 30],
...                [20, 25, 30, 0]])
(80, [0, 2, 3, 1])
>>> shortest_tour([[0, 1, 9],
...                [9, 0, 1],
...                [1, 9, 0]])        # one-way: 0 -> 1 -> 2 -> 0 costs 3, the other way 27
(3, [0, 1, 2])
>>> shortest_tour([[0]])
(0, [0])
```

In the first example `[0, 1, 3, 2]` (the same tour backwards) also costs 80; any order with the shortest length is accepted.

## Constraints

- `1 <= n <= 13`; times from 0 to 10**4.
- The tests compare with trying every order (`(n - 1)!` of them) only for `n <= 7`. For `n = 13` there are 479,001,600 orders, so you need the `O(2**n * n**2)` DP.

## Think about

1. What is `f[mask][last]`? Why is "which places are visited" not enough on its own, and why is the whole order not needed?
2. The answer is not `f[full][last]` itself. What must be added, and for which `last`?
3. To rebuild the order, what do you store (or re-derive) for every state, and in which direction do you walk?
4. Why does looping `mask` from 0 upwards fill every state before it is used?
