# Min cost climbing stairs

`cost[i]` is the price you pay when you step **from** stair `i`. You may start on stair 0 or on stair 1 for free. From stair `i` you pay `cost[i]` and move up 1 or 2 stairs. The top is just past the last stair, at index `n = len(cost)`. Write `min_cost_climb(cost)` that returns the cheapest total price to reach the top (chapter section 5).

## Example

```python
>>> min_cost_climb([10, 15, 20])                           # start on 1, pay 15, jump 2
15
>>> min_cost_climb([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])
6
>>> min_cost_climb([0, 0])
0
```

## Constraints

- `2 <= len(cost) <= 10**5`, `0 <= cost[i] <= 999`.
- Return an `int`, not a tuple or a table (the chapter's version returns both; this one returns only the price).
- `O(n)` time. A recursion `n` deep fails for `n = 10**5`.

## Think about

What is the state sentence? "The cheapest cost to **arrive** at stair `i`", where you have **not yet paid** `cost[i]`. Why does that make the base case `f(0) = f(1) = 0`?
