## Hint 1

`count` is the number of pairs `(i, m)` with `i >= 1`, `m >= 1`, `i * m <= n`. If both `i` and `m` were bigger than
`sqrt(n)`, the product would be bigger than `n`. So in every pair, at least one of them is at most `r = floor(sqrt(n))`.

## Hint 2

Let `side = n // 1 + n // 2 + ... + n // r`. That counts every pair with `i <= r`. By symmetry, `side` also counts every
pair with `m <= r`. Add the two, and subtract the pairs counted twice: those with both `i <= r` and `m <= r`.

## Hint 3

There are `r * r` pairs with both at most `r` (each of them has a product at most `r * r <= n`, so all are valid).
Answer: `2 * side - r * r`. Use `math.isqrt(n)` for an exact integer square root.
