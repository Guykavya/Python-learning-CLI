# The single number

A list has an odd number `n` of integers. Every value appears **exactly twice**, except one value that appears once.
Print that value.

The trick: `x ^ x == 0` and `x ^ 0 == x`, and XOR does not care about order. So XOR-ing the whole list cancels every pair
and leaves the single value.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One integer.

## Examples

| Input | Output | Why |
|---|---|---|
| `5` / `4 1 2 1 2` | `4` | 1 and 2 cancel |
| `1` / `9` | `9` | one number |
| `3` / `7 7 0` | `0` | the single value can be 0 |

## Constraints

- `1 <= n <= 999999` and `n` is odd
- `0 <= value < 2^30`

Use `input()` without a prompt message.
