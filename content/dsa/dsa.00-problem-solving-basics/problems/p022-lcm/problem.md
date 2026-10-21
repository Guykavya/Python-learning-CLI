# Least common multiple

The **least common multiple** (LCM) of two positive whole numbers `a` and `b` is the smallest positive
number that both `a` and `b` divide exactly. For example, the LCM of 4 and 6 is 12: the multiples of 4 are
4, 8, 12, 16, ... and the multiples of 6 are 6, 12, 18, ..., and 12 is the first number in both lists.

Read `a` and `b` and print their LCM.

The numbers can be as large as 10 to the power 18, so listing multiples one by one is far too slow.
Use the **greatest common divisor** (GCD): for positive `a` and `b`,

    lcm(a, b) = a / gcd(a, b) * b

and compute the GCD yourself with Euclid's algorithm. Do not import `math` (or anything else).

## Input

Two lines: `a`, then `b`. Use `input()` without a prompt message.

## Output

One line: the LCM of `a` and `b`, as an exact whole number (no `.0`, no rounding).

## Examples

| a | b | Output | Why |
|---|---|---|---|
| `4` | `6` | `12` | gcd is 2, 4 / 2 x 6 = 12 |
| `21` | `6` | `42` | gcd is 3, 21 / 3 x 6 = 42 |
| `7` | `7` | `7` | equal numbers |
| `1` | `9` | `9` | 1 divides everything |
| `5` | `20` | `20` | 5 already divides 20 |
| `8` | `9` | `72` | no common factor, so the LCM is the product |

## Constraints

- `1 <= a <= 1000000000000000000` (10 to the power 18)
- `1 <= b <= 1000000000000000000`
- The answer can be up to about 10 to the power 36. Python integers handle that exactly.
- Time limit: a few seconds.

## Before you code

Work Euclid's algorithm by hand for 21 and 6: replace the pair `(a, b)` with `(b, a % b)` until the second
number is 0. Then write your plan as comments at the top of `solution.py`.
