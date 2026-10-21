# Count the digits

Read one integer `n` and print how many digits it has.

The number may be negative or zero. The minus sign is not a digit, so `-450` has 3 digits.
The number `0` is written with one digit, so its answer is `1`.

**Rule:** do not convert the number to a string, and do not use `len()`. Use arithmetic only.

## Input

One line with an integer `n`.

## Output

One line with a single integer: the number of digits in `n`.

## Examples

| Input | Output |
|---|---|
| `2024` | `4` |
| `-450` | `3` |
| `0` | `1` |
| `7` | `1` |

## Constraints

- `n` can be negative, zero or positive.
- `n` can be very large, up to 50 digits long. Python integers handle this without any trouble.
- No `str()`, no `len()`, no `list()`.

Use `input()` without a prompt message.

## Before you code

Work `2024` and `0` by hand: how many times can you do `n // 10` before `n` becomes 0?
Write your plan as comments at the top of `solution.py`. Pay special attention to what your plan does for `0`.
