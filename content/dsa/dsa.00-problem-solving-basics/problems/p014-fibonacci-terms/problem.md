# First n Fibonacci terms

The Fibonacci sequence starts with `0` and `1`. Every later term is the sum of the two terms just before it:

```
0 1 1 2 3 5 8 13 21 34 ...
```

Read `n` and print the first `n` terms of this sequence.

## Input

One line with an integer `n`.

## Output

All `n` terms on **one line**, separated by single spaces, starting from `0`.
If `n` is 0, print nothing at all.

## Examples

| Input | Output |
|---|---|
| `7` | `0 1 1 2 3 5 8` |
| `1` | `0` |
| `2` | `0 1` |
| `0` | (nothing) |

## Constraints

- `0 <= n <= 90`
- The 90th term is `1779979416004714189`. Python integers are exact at that size; make sure your answer is too.

Use `input()` without a prompt message.

## Before you code

To produce the next term you need the two previous ones. Which two variables will you keep, and how do they change after each step?
Write your plan as comments at the top of `solution.py`, and check it on `n = 1` and `n = 2`.
