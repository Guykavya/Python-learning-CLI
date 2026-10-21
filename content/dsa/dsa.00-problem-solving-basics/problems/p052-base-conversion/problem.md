# Convert to any base from 2 to 16

We usually write numbers in base 10. In base `b`, each digit is worth `b` times the digit to its
right. For example, in base 2, `1101` means 1*8 + 1*4 + 0*2 + 1*1 = 13. Bases above 10 need more
digit symbols: base 16 uses `0`-`9` and then `A` (10), `B` (11), `C` (12), `D` (13), `E` (14), `F` (15).

Read an integer `n`, then a base `b`. Print `n` written in base `b`.

**Rules:**

- Do not use `bin()`, `hex()`, `oct()`, `format()` or `int(x, base)`. Compute the digits yourself.
- Get the character for a digit value `d` (0..15) with `"0123456789ABCDEF"[d]`.

## Input

Two lines: `n`, then `b`. Use `input()` without a prompt message.

## Output

- If `b` is not between 2 and 16 (inclusive), print exactly `invalid base`.
- Otherwise print `n` in base `b`: uppercase letters for digits above 9, no leading zeros, a leading
  `-` if `n` is negative, and just `0` when `n` is 0.

## Examples

| Input (n, b) | Output |
|---|---|
| `255`, `16` | `FF` |
| `255`, `2` | `11111111` |
| `-10`, `3` | `-101` |
| `0`, `7` | `0` |
| `42`, `10` | `42` |
| `42`, `1` | `invalid base` |
| `42`, `17` | `invalid base` |

## Constraints

- -10^18 <= n <= 10^18
- `b` is any integer (you must reject bad ones).

## Before you code

Convert 13 to base 2 by hand by dividing by 2 repeatedly and writing down the remainders.
In which order do the remainders come out, compared with the order you must print them?
Write your plan, including how you will handle 0 and negatives, as comments at the top of `solution.py`.
