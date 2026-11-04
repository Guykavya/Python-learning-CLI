# Exponent of a prime in `n!`

For each query `n p` (with `p` prime), print the exponent of `p` in the prime factorisation of `n!`: the largest `e` such that
`p^e` divides `n!`.

Example use: the number of trailing zeros of `n!` in base 10 equals the exponent of 5 in `n!` (there are always more 2s).

You cannot compute `n!` for `n = 10^18`. Count the multiples of `p` up to `n`, then multiples of `p^2` (they have one more
factor), and so on. This is **Legendre's formula**: `floor(n/p) + floor(n/p^2) + floor(n/p^3) + ...`

## Input

- Line 1: `q`.
- Then `q` lines, each with `n` and `p`.

## Output

For each query, one line: the exponent.

## Example

Input:

```
4
10 2
100 5
10 7
1000000000000000000 5
```

Output:

```
8
24
1
249999999999999995
```

`10! = 3628800 = 2^8 * 3^4 * 5^2 * 7`. For `100!`: `100//5 + 100//25 = 20 + 4 = 24` trailing zeros.

## Constraints

- `1 <= q <= 100000`
- `0 <= n <= 10^18`, `p` is a prime with `2 <= p <= 10^18`

Use `input()` without a prompt message.
