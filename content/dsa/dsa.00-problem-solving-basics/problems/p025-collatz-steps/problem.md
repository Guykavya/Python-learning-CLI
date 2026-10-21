# Collatz steps and peak

Start from a positive whole number `n` and repeat this rule until the number becomes 1:

- if the number is even, halve it;
- if the number is odd, replace it with three times the number plus one.

For example, starting from 6: 6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1. That took 8 steps,
and the largest value seen along the way was 16.

Read `n` and print how many steps it takes to reach 1, and the largest value reached
(the **peak**). The starting number itself counts for the peak, so for `n = 8` the peak is 8.
If `n` is already 1, no steps are needed.

(Nobody has proved that every starting number reaches 1, but it has been checked far beyond the numbers used here.)

## Input

One line: the number `n`. Use `input()` without a prompt message.

## Output

Exactly two lines:

```
steps S
peak P
```

where `S` is the number of steps and `P` the peak, both as whole numbers (no `.0`).

## Examples

| Input | Output |
|---|---|
| `6` | `steps 8` / `peak 16` |
| `1` | `steps 0` / `peak 1` |
| `8` | `steps 3` / `peak 8` |
| `27` | `steps 111` / `peak 9232` |

## Constraints

- `1 <= n <= 1000000000000` (10 to the power 12)
- Along the way the numbers can grow much larger than `n` (more than 20 digits). Keep them as exact integers.

## Before you code

Write out the sequence for `n = 7` by hand and count the steps (you should get 16, with peak 52).
Then write your plan as comments at the top of `solution.py`.
