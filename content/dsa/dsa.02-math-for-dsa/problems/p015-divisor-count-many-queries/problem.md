# Divisor counts for many queries

If `n = p1^e1 * p2^e2 * ... * pk^ek`, then the number of divisors of `n` is `(e1 + 1) * (e2 + 1) * ... * (ek + 1)`.
(Each divisor picks an exponent from `0` to `ei` for each prime.) For example `360 = 2^3 * 3^2 * 5^1` has
`4 * 3 * 2 = 24` divisors.

You get many numbers up to 10^6 and must print the divisor count of each. Factorising each query by trial
division costs up to 1000 steps, times 100000 queries is too slow. Instead build an **smallest prime factor**
table once: `spf[x]` is the smallest prime dividing `x`. Then you can factorise any `x` by repeatedly
reading `spf[x]` and dividing: that takes only as many steps as `x` has prime factors (at most about 20).

Build `spf` with a sieve: start with `spf[x] = x`; for each prime `p` with `p * p <= N`, for multiples
`m = p*p, p*p + p, ...` set `spf[m] = p` if it still equals `m`.

## Input

- Line 1: `q`.
- The next `q` lines: one integer `n` each.

## Output

`q` lines: the number of divisors of each `n`.

## Example

Input:

```
4
360
97
1
64
```

Output:

```
24
2
1
7
```

## Constraints

- `1 <= q <= 100000`
- `1 <= n <= 10^6`

Read the input all at once with `sys.stdin.read().split()`.
