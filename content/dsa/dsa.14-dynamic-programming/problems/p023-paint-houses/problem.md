# Paint houses

A row of houses must each be painted red, green or blue. `costs[i]` is a list of three numbers: the price of painting house `i` with colour 0, 1 or 2. **No two neighbouring houses may have the same colour.** Write `min_paint_cost(costs)` that returns the cheapest total.

## Example

```python
>>> min_paint_cost([[17, 2, 17], [16, 16, 5], [14, 3, 19]])
10
>>> min_paint_cost([[1, 2, 100], [1, 100, 100]])
3
>>> min_paint_cost([[7, 6, 2]])
2
>>> min_paint_cost([])
0
```

First example: green (2), blue (5), green (3) = 10. Second: house 0 takes its **second** cheapest colour (2) so that house 1 can take colour 0 (1).

## Constraints

- `0 <= len(costs) <= 400`, every cost is an integer in `0 .. 1000`.
- Try for `O(1)` extra memory: three rolling variables (section 6). The tests check the result and the time, not the memory.

## Think about

1. Is "the cheapest way to paint the first `i` houses" enough as a state? To paint house `i` you must know one more thing about house `i - 1`. What?
2. Add that thing to the state: `f[i][c]` = the cheapest way to paint houses `0..i` **with house `i` painted colour `c`**. What is the transition?
3. Why does taking the cheapest colour for each house, one by one, fail on the second example?
