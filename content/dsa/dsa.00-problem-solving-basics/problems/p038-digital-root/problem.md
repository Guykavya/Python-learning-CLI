# Digital root

Read a whole number `n`. While `n` has more than one digit, replace it with the sum of its digits.
When it has a single digit, stop. That last digit is the **digital root**.

Also count the **rounds**: how many times you replaced `n` with its digit sum.

**Rule:** use arithmetic only (`%` and `//`). Do not convert the number to a string.

## Input

One line with the integer `n`.

## Output

Two lines, exactly:

```
root R
rounds K
```

## Examples

| Input | Output | Why |
|---|---|---|
| `38` | `root 2` / `rounds 2` | 38 -> 3 + 8 = 11 -> 1 + 1 = 2 |
| `99` | `root 9` / `rounds 2` | 99 -> 18 -> 9 |
| `9` | `root 9` / `rounds 0` | already one digit, nothing to do |
| `0` | `root 0` / `rounds 0` | already one digit |

(`/` in the table separates the two output lines.)

## Constraints

- `0 <= n`, and `n` has at most 100 digits. Python integers can hold that exactly.
- Use `input()` without a prompt message.

## Before you code

There are two loops here: one that adds up the digits, and one that repeats that whole job.
Write which loop is inside which, and the stopping condition of each, as comments at the top of `solution.py`.
Then trace `99` and `0` through your plan.
