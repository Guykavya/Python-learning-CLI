# Decimal to binary by hand

Computers store numbers in **binary** (base 2), using only the digits 0 and 1. Each position is worth
twice the one to its right: from the right, the positions are worth 1, 2, 4, 8, 16, and so on.
For example `1101` in binary is 8 + 4 + 0 + 1 = 13.

Read a whole number `n` (0 or more) and print it in binary, with no leading zeros. `0` is printed as `0`.

**Rule:** build the answer yourself using repeated division by 2. Do not use `bin()`, `format()`, `hex()`,
`oct()`, or format specs like `f"{n:b}"`.

## Input

One line: the number `n`. Use `input()` without a prompt message.

## Output

One line: the binary digits of `n`, most significant digit first, no leading zeros, no `0b` prefix.

## Examples

| Input | Output |
|---|---|
| `13` | `1101` |
| `6` | `110` |
| `1` | `1` |
| `0` | `0` |
| `1024` | `10000000000` |

## Constraints

- `0 <= n <= 1000000000000000000` (10 to the power 18)

## Before you code

Divide 13 by 2 again and again by hand, writing the remainder each time, until the number becomes 0.
In which order do the remainders appear, compared with the order you must print them?
Write your plan as comments at the top of `solution.py`.
