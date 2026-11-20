## Hint 1

`f(i, j)` = (the mover's stones) minus (the other player's stones) from the range `i..j` onward, when both play perfectly. With one pile, `f(i, i) = piles[i]`. The answer is `f(0, n - 1)` (and 0 for no piles).

## Hint 2

If the mover takes `piles[i]`, the other player becomes the mover on `i+1..j` and gains `f(i+1, j)` **over** the first player. So the first player's difference is `piles[i] - f(i+1, j)`. Taking the right pile gives `piles[j] - f(i, j-1)`. The mover picks the larger:

`f(i, j) = max(piles[i] - f(i+1, j), piles[j] - f(i, j-1))`.

## Hint 3

```
f = n x n table; f[i][i] = piles[i]
for length in 2..n:
    for i in 0..n-length:
        j = i + length - 1
        f[i][j] = max(piles[i] - f[i+1][j], piles[j] - f[i][j-1])
return f[0][n-1]     (0 if there are no piles)
```
