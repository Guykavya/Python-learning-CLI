# Prime factorisation

Every integer `n >= 2` is a product of primes in exactly one way (apart from the order). For example
`360 = 2^3 * 3^2 * 5`. For each query print the factorisation as `p^e` pairs, with the primes in increasing
order, separated by single spaces. Write the exponent even when it is 1 (`5^1`). For `n = 1` print `1`.

The method: try `i = 2, 3, 4, ...`. Whenever `i` divides `n`, divide it out as many times as you can and count
the exponent. Stop when `i * i > n` (use the **current**, already reduced `n`). If something larger than 1 is left,
it is a prime factor too.

## Input

- Line 1: `q`.
- The next `q` lines: one integer `n` each.

## Output

`q` lines, each a factorisation in the format above.

## Example

Input:

```
3
360
97
1
```

Output:

```
2^3 3^2 5^1
97^1
1
```

## Constraints

- `1 <= q <= 5`
- `1 <= n <= 10^12`

Trying every `i` up to `n` is impossible here. Up to the square root of `n` is at most 10^6 steps.

Use `input()` without a prompt message.
