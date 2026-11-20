## Approach

The state needs the colour of the last house, because that is what the next house must avoid:

- **State:** `f[i][c]` = the cheapest cost of painting houses `0..i` with house `i` painted `c`.
- **Transition:** `f[i][c] = costs[i][c] + min(f[i-1][d] for d != c)`.
- **Base:** `f[0][c] = costs[0][c]`.
- **Answer:** `min(f[n-1])`; `0` when there are no houses.

Row `i` reads only row `i - 1`, so three rolling variables replace the table (section 6).

```python
def min_paint_cost(costs):
    if not costs:
        return 0
    red, green, blue = costs[0]           # f[0][c]: house 0 painted colour c
    for c0, c1, c2 in costs[1:]:
        red, green, blue = (c0 + min(green, blue),
                            c1 + min(red, blue),
                            c2 + min(red, green))
    return min(red, green, blue)
```

Trace `[[17, 2, 17], [16, 16, 5], [14, 3, 19]]`: start `(17, 2, 17)`; then `(16 + 2, 16 + 17, 5 + 2) = (18, 33, 7)`; then `(14 + 7, 3 + 7, 19 + 18) = (21, 10, 37)`. Answer 10.

## Complexity

`O(n)` time, `O(1)` extra space.

## Another way

With `k` colours, write the inner step as a loop: `new[c] = costs[i][c] + min(prev[d] for d in range(k) if d != c)`, which is `O(n * k^2)`. To make it `O(n * k)`, keep the smallest and the second smallest value of `prev`: for colour `c` use the smallest, unless it belongs to `c` itself, then use the second smallest.

A top-down version, `best(i, c)` with `functools.cache`, also passes: 400 houses means a recursion depth of 400 (twice that in frames if you call it inside a generator expression).
