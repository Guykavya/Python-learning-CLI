# Is it prime?

A **prime** is a whole number greater than 1 whose only positive divisors are 1 and itself.
So 2, 3, 5, 7, 11 are prime; 4 (= 2 x 2), 9 (= 3 x 3) and 15 (= 3 x 5) are not.
By this definition 0, 1 and every negative number are **not** prime. 2 is the only even prime.

Read one whole number `n` and say whether it is prime.

The numbers can be as large as a trillion, so trying every possible divisor from 2 up to `n` is far
too slow. Your program must answer within a few seconds even for 12-digit primes.

## Input

One line: the number `n`. Use `input()` without a prompt message.

## Output

Exactly one line: `prime` or `not prime` (lowercase, one space in `not prime`).

## Examples

| Input | Output | Why |
|---|---|---|
| `7` | `prime` | only 1 and 7 divide it |
| `91` | `not prime` | 91 = 7 x 13 |
| `2` | `prime` | the smallest prime |
| `1` | `not prime` | primes must be greater than 1 |
| `-7` | `not prime` | negatives are never prime |
| `49` | `not prime` | 49 = 7 x 7, a perfect square |

## Constraints

- `-1000000000000 <= n <= 1000000000000` (up to 10 to the power 12)
- Time limit: a few seconds for any allowed `n`.

## Before you code

If `n = a x b` and both `a` and `b` were bigger than the square root of `n`, what would `a x b` be?
Use that idea to decide where your divisor search can stop. Write your plan as comments at the top of `solution.py`.
