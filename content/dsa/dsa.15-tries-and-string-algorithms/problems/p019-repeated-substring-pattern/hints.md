## Hint 1

If `s` is a block of length `p` repeated, then `p` is a period of `s` and divides `n`. The smallest period is `p = n - pi[n - 1]` (p017).

## Hint 2

The answer is `(s[:p], n // p)` when `n % p == 0` and `p < n`; otherwise `(s, 1)`. (If `p` does not divide `n`, no period that divides `n` exists except `n` itself: by a classic lemma, two periods `p` and `q` with `p + q <= n` imply the period `gcd(p, q)`.)

## Hint 3

```
pi = prefix_function(s)
p = n - pi[-1]
if p < n and n % p == 0: return s[:p], n // p
return s, 1
```
