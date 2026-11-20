# nCr mod p with precomputed factorials

Answer many binomial-coefficient queries modulo `p = 10**9 + 7`: `C(n, r) mod p`, where `C(n, r)` is the number of ways to choose `r` items from `n`. If `r > n` the answer is `0`.

## Input

The first line holds `q` (`1 <= q <= 10**5`). Each of the next `q` lines holds `n r` (`0 <= n <= 10**6`, `0 <= r <= 10**6`).

## Output

One answer per line.

## Example

```text
5
5 2
10 0
10 10
3 5
0 0
```
```text
10
1
1
0
1
```

## The catch

Computing each `C(n, r)` with a loop costs up to `10**6` steps per query: `10**11` steps in total. Precompute `fact[i] = i! mod p` once, and `inv_fact[i]`, then each query is two multiplications (chapter section 11).
