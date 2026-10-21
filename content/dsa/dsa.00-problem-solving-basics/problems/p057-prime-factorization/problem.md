# Prime factorization

Every whole number greater than 1 can be written as a product of primes in exactly one way (up to
order). For example 360 = 2 * 2 * 2 * 3 * 3 * 5 = 2^3 * 3^2 * 5.

Read `n` and print its prime factorization.

## Input

One line: the integer `n`. Use `input()` without a prompt message.

## Output

One line in exactly this format:

```
n = f1 * f2 * ...
```

- Each factor is a prime `p` written as `p` if it appears once, or as `p^e` if it appears `e > 1` times.
- Primes are in increasing order, separated by ` * ` (space, star, space).
- There is a space on each side of `=`.

## Examples

| Input | Output |
|---|---|
| `360` | `360 = 2^3 * 3^2 * 5` |
| `13` | `13 = 13` |
| `1024` | `1024 = 2^10` |
| `2` | `2 = 2` |
| `999966000289` | `999966000289 = 999983^2` |

## Constraints

- 2 <= n <= 10^12
- Time limit: 5 seconds, even when `n` is a prime close to 10^12.

## Before you code

Factor 360 by hand: divide by 2 as long as you can, then by 3, and so on. Write down what you
divide by and how many times. Then think about 999999999989, which is prime: how far do you need
to try divisors before you can be sure? Write your plan as comments at the top of `solution.py`,
including how you will build the output text.
