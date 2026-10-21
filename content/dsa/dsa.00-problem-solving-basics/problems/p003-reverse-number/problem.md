# Reverse a number

Read one integer `n` and print the integer you get by writing its digits in reverse order.

- Zeros that end up at the front disappear, because the result is printed as a normal integer. So `1200` becomes `21`.
- A negative number stays negative: reverse the digits and keep the minus sign. So `-123` becomes `-321`.
- `0` stays `0`.

**Rule:** do not convert the number to a string. Use arithmetic only.

## Input

One line with an integer `n`.

## Output

One line with the reversed integer.

## Examples

| Input | Output |
|---|---|
| `1234` | `4321` |
| `1200` | `21` |
| `-123` | `-321` |
| `0` | `0` |
| `7` | `7` |

## Constraints

- `n` can be negative, zero or positive, and up to 30 digits long.
- No `str()`, no `list()`, no `reversed()`.

Use `input()` without a prompt message.

## Before you code

Reverse `1234` by hand, but only using `% 10`, `// 10` and multiplying by 10. Write each step down.
Then write your plan as comments at the top of `solution.py`.
