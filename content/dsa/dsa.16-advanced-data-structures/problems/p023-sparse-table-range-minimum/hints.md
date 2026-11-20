## Hint 1

`table[0] = a`; `table[k][i] = min(table[k-1][i], table[k-1][i + 2**(k-1)])`: a block of length `2**k` is two halves of length `2**(k-1)`. Build rows while `2**k <= n`.

## Hint 2

For a range of length `L = r - l`, take the largest `k` with `2**k <= L`. The blocks `[l, l + 2**k)` and `[r - 2**k, r)` together cover `[l, r)`; they may overlap, and `min(x, x) = x` makes the overlap harmless.

## Hint 3

Precompute `lg[1] = 0`, `lg[L] = lg[L // 2] + 1`. Then `query(l, r)`: `k = lg[r - l]`; `return min(table[k][l], table[k][r - (1 << k)])`.
