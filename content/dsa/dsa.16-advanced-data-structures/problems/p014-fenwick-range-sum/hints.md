## Hint 1

`prefix(r)` is the sum of the first `r` elements, `a[0:r]`. The elements `a[l:r]` are the first `r` minus the first `l`: `prefix(r) - prefix(l)`. That is why half-open ranges need no `- 1`.

## Hint 2

`get(i) = range_sum(i, i + 1)`, and `set(i, v) = add(i, v - get(i))`: add the difference.

## Hint 3

Linear build: put `a[k - 1]` into `t[k]` for every `k`. Going `k = 1, 2, ..., n`, cell `k` is complete when you reach it (all its smaller pieces were already added); add it into its parent `k + (k & -k)` if that is `<= n`. Each cell is pushed once: `O(n)`.
