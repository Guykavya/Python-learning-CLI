# nCr modulo 10^9 + 7 with factorial tables

`C(n, r) = n! / (r! * (n - r)!)`. With `n` up to 10^6 the true value has hundreds of thousands of digits, so
we ask for it **modulo `p = 10^9 + 7`**. You cannot divide remainders as ordinary numbers. Use the **modular inverse**:
since `p` is prime, Fermat's little theorem says `x^(p-1) = 1 (mod p)`, so `x^(p-2)` is the inverse of `x`:
`x * x^(p-2) = 1 (mod p)`.

Plan (many queries, so precompute once):

1. `fact[i] = i! mod p` for `i = 0..N`.
2. `inv_fact[N] = fact[N]^(p-2) mod p` (one modular power).
3. `inv_fact[i - 1] = inv_fact[i] * i mod p`, going down from `N` to 1. (Because `1/(i-1)! = i / i!`.)
4. Each query: `fact[n] * inv_fact[r] % p * inv_fact[n - r] % p`, and 0 when `r > n`.

Here `N` is the largest `n` among the queries.

## Input

- Line 1: `q`.
- The next `q` lines: two integers `n r`.

## Output

`q` lines: `C(n, r) mod 1000000007`.

## Example

Input:

```
4
5 2
10 3
100 50
7 9
```

Output:

```
10
120
538992043
0
```

## Constraints

- `1 <= q <= 100000`
- `0 <= n <= 10^6`, `0 <= r <= 10^6`

Read the input all at once with `sys.stdin.read().split()`.
