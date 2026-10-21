# Second largest, one pass

Read a count `n`, then `n` whole numbers. Print the **second largest distinct value**: the biggest value
that is strictly smaller than the maximum.

Duplicates do not count twice. For `5 5 3` the largest value is 5, and the second largest distinct value is 3
(not 5). If there are fewer than two different values (for example `n = 1`, or all numbers equal), print `none`.

**Rule:** do not store the numbers. No lists, no `sorted()`, no `set()`. Read each number once, update a few
variables, and move on. (This is how you would handle a stream of millions of numbers.)

## Input

- Line 1: `n`, how many numbers follow.
- Then `n` lines, one whole number on each.

Use `input()` without a prompt message.

## Output

One line: the second largest distinct value, or `none`.

## Examples

| Numbers (after n) | Output | Why |
|---|---|---|
| `4 9 2 7` | `7` | the largest is 9, the next is 7 |
| `5 5 3` | `3` | the two 5s are the same value |
| `3 1 8` | `3` | the max comes last, so 3 must move down to second |
| `6 6 6` | `none` | only one distinct value |
| `42` (n = 1) | `none` | only one number |
| `-4 -1 -7` | `-4` | negatives work the same way |

(In the real input each number is on its own line, after the line with `n`.)

## Constraints

- `1 <= n <= 100000`
- Each number is between `-1000000000` and `1000000000`.

## Before you code

Decide which variables you will keep while reading, and what happens to each of them when the new number is
(a) bigger than the current largest, (b) equal to it, (c) between the two, (d) smaller than both.
Write that plan as comments at the top of `solution.py`.
