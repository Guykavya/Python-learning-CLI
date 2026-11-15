## Hint 1

"Everything except `a[i]`" is two pieces: everything to the **left** of `i` and everything to the **right** of `i`.
Can you get all the left products in one pass, the way you built prefix sums?

## Hint 2

Walk left to right with `left = 1`: store `left` as the answer for `i`, **then** multiply `left` by `a[i]`. Walk right
to left with `right = 1`: multiply the stored answer by `right`, then multiply `right` by `a[i]`. Take `% MOD` after
every multiplication so the numbers stay small.

## Hint 3

```
ans = [1] * n; left = 1
for i in 0..n-1: ans[i] = left; left = left * a[i] % MOD
right = 1
for i in n-1..0: ans[i] = ans[i] * right % MOD; right = right * a[i] % MOD
print ans
```
