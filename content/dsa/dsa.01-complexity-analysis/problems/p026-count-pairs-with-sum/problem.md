# Count the pairs that make the target

Read `n` integers and a target `t`. Count the pairs of positions `i < j` with `a[i] + a[j] == t`.

This time there is no slow program to start from. Design the solution yourself, starting from the constraints.

## Input

- Line 1: `n` and `t`.
- Line 2: `n` integers.

## Output

One line with one integer: the number of pairs.

## Examples

| Input | Output | Why |
|---|---|---|
| `5 6` / `1 5 3 3 7` | `2` | (1, 5) and (3, 3); the two 3s are different positions |
| `4 4` / `2 2 2 2` | `6` | every pair of the four 2s: 4 * 3 / 2 |
| `3 10` / `5 1 2` | `0` | 5 + 5 needs two positions holding 5 |
| `4 0` / `-1 1 -1 1` | `4` | each -1 pairs with each 1 |

## Constraints

- `1 <= n <= 200000`
- every value and `t` are between `-10^9` and `10^9`

Use `input()` without a prompt message.

## Before you code

1. How many pairs could there be at most? Could the answer be bigger than `n`? (Look at the second example.)
2. From the constraints, what is the slowest complexity that will finish in about a second in Python?
3. Write your plan in `solution.py` as comments, then the code.
