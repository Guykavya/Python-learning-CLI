# Sum of the first n numbers

Read a whole number `n` and print the sum `1 + 2 + 3 + ... + n`.

If `n` is `0`, there is nothing to add, so the sum is `0`.

## Input

One line with an integer `n`.

## Output

One line with a single integer: the sum of all whole numbers from 1 to `n`.

## Examples

| Input | Output | Why |
|---|---|---|
| `5` | `15` | 1 + 2 + 3 + 4 + 5 |
| `1` | `1` | just 1 |
| `0` | `0` | nothing to add |
| `10` | `55` | 1 + 2 + ... + 10 |

## Constraints

- `0 <= n <= 1000000`

Use `input()` without a prompt message.

## Before you code

Work `n = 4` by hand: write down the running total after each number is added.
Then write your plan as comments at the top of `solution.py`. Check that your `range(...)` really includes `n`.
