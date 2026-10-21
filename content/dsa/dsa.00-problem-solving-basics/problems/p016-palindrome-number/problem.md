# Palindrome number

A number is a *palindrome* if its digits read the same from left to right and from right to left.
`121`, `1221` and `7` are palindromes. `123` and `10` are not.

Read an integer `n` and print `yes` if it is a palindrome, otherwise `no`.

**Negative numbers are never palindromes** in this problem: `-121` reads as `121-` backwards, which is different. So any negative input prints `no`.

**Rule:** do not convert the number to a string. Use arithmetic only.

## Input

One line with an integer `n`.

## Output

One line: `yes` or `no` (lowercase).

## Examples

| Input | Output | Why |
|---|---|---|
| `121` | `yes` | same both ways |
| `1221` | `yes` | same both ways |
| `10` | `no` | backwards it is `01`, which is not `10` |
| `0` | `yes` | a single digit |
| `-121` | `no` | negative numbers are never palindromes |
| `1000021` | `no` | backwards it is `1200001` |

## Constraints

- `-10^18 <= n <= 10^18`
- No `str()`, no `list()`, no `reversed()`.

Use `input()` without a prompt message.

## Before you code

You already reversed a number in an earlier problem. How can that help here? Be careful: the loop destroys `n`.
Write your plan as comments at the top of `solution.py`.
