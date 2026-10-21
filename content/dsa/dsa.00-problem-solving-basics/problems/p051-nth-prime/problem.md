# The k-th prime

A prime is a whole number greater than 1 whose only divisors are 1 and itself. The primes in
order are 2, 3, 5, 7, 11, 13, ... so the 1st prime is 2, the 4th is 7 and the 6th is 13.

Read `k` and print the `k`-th prime.

The catch: `k` can be 20000, and the 20000th prime is above 200000. Checking each candidate by
dividing it by every smaller number is far too slow. Your program must finish within a few seconds.

## Input

One line: the integer `k`. Use `input()` without a prompt message.

## Output

One line: the `k`-th prime.

## Examples

| Input | Output |
|---|---|
| `1` | `2` |
| `2` | `3` |
| `6` | `13` |
| `100` | `541` |
| `10000` | `104729` |

## Constraints

- 1 <= k <= 20000
- Time limit: 10 seconds for `k = 20000` (a good solution takes under a second).

## Before you code

This needs two loops: an outer loop that walks through candidates and counts primes, and an inner
loop that tests one candidate. Plan them separately. For the inner loop, answer on paper: if `x` has
a divisor larger than its square root, what must the other divisor look like? Write the plan as
comments at the top of `solution.py`.
