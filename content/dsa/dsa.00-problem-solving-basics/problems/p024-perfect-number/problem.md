# Perfect, abundant or deficient

The **proper divisors** of a positive whole number `n` are all its positive divisors except `n` itself.
For 12 they are 1, 2, 3, 4, 6. Add them up and compare the sum with `n`:

- sum equal to `n`: the number is **perfect** (6 = 1 + 2 + 3)
- sum bigger than `n`: the number is **abundant** (12: 1 + 2 + 3 + 4 + 6 = 16 > 12)
- sum smaller than `n`: the number is **deficient** (8: 1 + 2 + 4 = 7 < 8)

The number 1 has no proper divisors at all, so its sum is 0 and it is deficient.

Read `n` and print which of the three it is.

Numbers go up to 10 to the power 12, so trying every possible divisor from 1 to `n` is far too slow.
Divisors come in **pairs**: if `d` divides `n`, so does `n // d`. Use this to search only up to the square root.

## Input

One line: the number `n`. Use `input()` without a prompt message.

## Output

Exactly one line: `perfect`, `abundant` or `deficient` (lowercase).

## Examples

| Input | Proper divisors | Sum | Output |
|---|---|---|---|
| `6` | 1, 2, 3 | 6 | `perfect` |
| `12` | 1, 2, 3, 4, 6 | 16 | `abundant` |
| `8` | 1, 2, 4 | 7 | `deficient` |
| `36` | 1, 2, 3, 4, 6, 9, 12, 18 | 55 | `abundant` |
| `1` | (none) | 0 | `deficient` |
| `2` | 1 | 1 | `deficient` |

Note `36`: its divisor 6 pairs with itself (6 x 6 = 36), so it must be added only **once**.

## Constraints

- `1 <= n <= 1000000000000` (10 to the power 12)
- Time limit: a few seconds.

## Before you code

List the divisor pairs of 36 by hand: (1, 36), (2, 18), (3, 12), (4, 9), (6, 6). Which ones belong in the sum,
and where can your search stop? Write your plan as comments at the top of `solution.py`.
