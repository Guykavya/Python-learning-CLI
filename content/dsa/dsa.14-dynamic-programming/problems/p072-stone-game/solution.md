## Approach

The remaining piles are always a range `i..j`, so the state is a range. To avoid storing whose turn it is, measure everything **from the point of view of the player about to move** (the "negamax" idea).

- State: `f(i, j)` = best (mover's stones minus opponent's stones) on the range `i..j`.
- Transition: taking the left pile earns `piles[i]`, and then the opponent, now the mover, gets `f(i+1, j)` more than us. So `f(i, j) = max(piles[i] - f(i+1, j), piles[j] - f(i, j-1))`.
- Base: `f(i, i) = piles[i]`. Order: by length. Answer: `f(0, n - 1)`.

```python
def stone_game(piles):
    n = len(piles)
    if n == 0:
        return 0
    f = [[0] * n for _ in range(n)]
    for i in range(n):
        f[i][i] = piles[i]                      # one pile left: take it
    for length in range(2, n + 1):              # short rows of piles first
        for i in range(n - length + 1):
            j = i + length - 1
            f[i][j] = max(piles[i] - f[i + 1][j],    # take the left pile
                          piles[j] - f[i][j - 1])    # take the right pile
    return f[0][n - 1]
```

For `[2, 7, 3]`: `f[0][1] = max(2 - 7, 7 - 2) = 5`, `f[1][2] = max(7 - 3, 3 - 7) = 4`, `f[0][2] = max(2 - f[1][2], 3 - f[0][1]) = max(-2, -2) = -2`. Whatever the first player takes, the second takes the 7.

## Complexity

`O(n^2)` states, `O(1)` work each: `O(n^2)` time and memory (`O(n)` memory with one rolling row, since a range of length `L` needs only ranges of length `L - 1`).

## Another way

Keep two values per state: the best score of the player to move, and the total of the range (with prefix sums). Then `best(i, j) = total(i, j) - min(best(i+1, j), best(i, j-1))`: "I get everything except what my opponent gets from the smaller range." It is the same DP; the difference version above is shorter. Top-down with `@functools.cache` works too, with a recursion depth of at most 500.
