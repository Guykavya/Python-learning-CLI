# Primes in a far-away range

Read `l` and `r`. Print how many primes are in `l..r`, and their sum.

`r` can be 10^10, far too big for an ordinary sieve (10^10 bytes of memory). But `r - l` is at most 10^6. The idea of the
**segmented sieve**: every composite number up to `r` has a prime factor `p` with `p * p <= r`, so

1. sieve normally up to `sqrt(r)` (at most 10^5) to get the *base primes*;
2. make a table for just `l..r` (index `j` means the number `l + j`);
3. for each base prime `p`, cross off its multiples in `l..r`, starting at `max(p*p, first multiple of p that is >= l)`.

The numbers 0 and 1 are not prime, so be careful when `l` is 0 or 1.

## Input

One line: `l r`.

## Output

Two lines: the count of primes in `l..r`, and their sum.

## Examples

| Input | Output | Why |
|---|---|---|
| `1 10` | `4` / `17` | primes 2, 3, 5, 7 |
| `10 20` | `4` / `60` | 11, 13, 17, 19 |
| `24 28` | `0` / `0` | 24, 25, 26, 27, 28 are all composite |
| `9999999900 10000000000` | `3` / `29999999839` | 9999999929, 9999999943, 9999999967 |

## Constraints

- `0 <= l <= r <= 10^10`, `r - l <= 10^6`

Use `input()` without a prompt message. Do not use floats to get the square root: find the smallest `limit` with
`limit * limit > r` by a small loop, or by `(r ** 0.5)` followed by a correcting loop.
