# Binary to decimal with validation

Read one line of text. If it is a valid binary number (every character is `0` or `1`), print its value in
decimal. Otherwise print `invalid`.

In binary each position is worth twice the one to its right, so `1101` is 8 + 4 + 0 + 1 = 13.
Leading zeros are allowed and change nothing: `0001` is 1.

**Rule:** go through the characters yourself with `for ch in s` and build the value with arithmetic.
Do not use `int(s, 2)` or any string methods (`.isdigit()`, `.count()`, `.strip()`, ...).
Comparing a character with `==` is fine.

## Input

One line of 1 to 64 characters. It may contain anything (letters, digits, spaces, signs).
Read it with `s = input()`, without a prompt message.

## Output

One line: the decimal value, or `invalid` if any character is not `0` or `1`.

## Examples

| Input | Output | Why |
|---|---|---|
| `1101` | `13` | 8 + 4 + 0 + 1 |
| `0001` | `1` | leading zeros do not matter |
| `0` | `0` | |
| `102` | `invalid` | `2` is not a binary digit |
| `abc` | `invalid` | not digits at all |
| `10 1` | `invalid` | a space is not a binary digit |

## Constraints

- The line has between 1 and 64 characters.
- With 64 ones the value is 18446744073709551615. Python integers handle this exactly.

## Before you code

Work out `1101` reading the digits **left to right**: start with 0, and for each digit double what you have and
add the digit. Check that you reach 13. Then write your plan as comments at the top of `solution.py`.
