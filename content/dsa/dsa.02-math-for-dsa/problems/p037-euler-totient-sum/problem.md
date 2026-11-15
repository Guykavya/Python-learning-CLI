# Euler's phi and the gcd sum

For each query `n`, print two numbers:

- `phi(n)`: how many `i` in `1..n` have `gcd(i, n) = 1`;
- `S(n)`: the sum of `gcd(i, n)` over `i = 1..n`.

Both are *multiplicative*: if `a` and `b` are coprime, `f(a*b) = f(a) * f(b)`. So factorise `n = p1^e1 * p2^e2 ...` and combine:

- `phi(p^e) = p^(e-1) * (p - 1)`
- `S(p^e) = p^(e-1) * (e * (p - 1) + p)`

Check `S(2) = gcd(1,2) + gcd(2,2) = 3`: the formula gives `1 * (1*1 + 2) = 3`. And `S(4) = 1 + 2 + 1 + 4 = 8`: the formula gives
`2 * (2*1 + 2) = 8`.

Factorising each query by trial division would be slow for 10^5 queries. Build the **smallest prime factor** table once for
all numbers up to 10^6, then factorise each query by repeatedly dividing by `spf[n]`.

## Input

- Line 1: `q`.
- Then `q` lines, each with `n`.

## Output

For each query, one line `phi(n) S(n)`.

## Example

Input:

```
4
1
12
13
36
```

Output:

```
1 1
4 40
12 25
12 168
```

For `n = 12`: the numbers coprime to 12 are 1, 5, 7, 11, so `phi = 4`. The gcds are 1,2,3,4,1,6,1,4,3,2,1,12: sum 40. For the prime 13: `phi = 12`, and `S = 12 * 1 + 13 = 25`.

## Constraints

- `1 <= q <= 100000`
- `1 <= n <= 10^6`

Use `input()` without a prompt message.
