# GCD with Euclid's algorithm

The greatest common divisor (GCD) of two integers is the largest whole number that divides both of them with no remainder.
For example, the GCD of 12 and 18 is 6.

Read two integers `a` and `b` and print their GCD, using **Euclid's algorithm**:

> The GCD of `a` and `b` is the same as the GCD of `b` and `a % b`. Keep replacing the pair until the second number is 0.
> The first number is then the answer.

For example: (48, 18) -> (18, 12) -> (12, 6) -> (6, 0), so the GCD is 6.

Details:

- The answer is never negative. Signs do not matter: the GCD of -12 and 18 is 6.
- The GCD of 0 and any number `x` is the size of `x`, because every number divides 0. So the GCD of 0 and 5 is 5.
- The two numbers will never both be 0.

**Rules:** do not import anything (no `math.gcd`) and do not call any function named `gcd`. Write the loop yourself.
The numbers can be as large as 10^18, so a slow method (subtracting again and again, or trying every possible divisor) will run out of time.

## Input

Two lines:

1. the integer `a`
2. the integer `b`

## Output

One line with the GCD of `a` and `b`, a non-negative integer.

## Examples

| `a` | `b` | Output |
|---|---|---|
| `48` | `18` | `6` |
| `-12` | `18` | `6` |
| `0` | `5` | `5` |
| `17` | `5` | `1` |

## Constraints

- `-10^18 <= a, b <= 10^18`
- `a` and `b` are not both 0.
- Your program must finish within 3 seconds on every test.

Use `input()` without a prompt message.

## Before you code

Run Euclid's algorithm by hand on (48, 18) and on (0, 5). Write the pair after each step.
What do you do with negative numbers before you start? Write your plan as comments at the top of `solution.py`.
