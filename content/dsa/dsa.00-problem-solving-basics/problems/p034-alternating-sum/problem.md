# Alternating sum with a huge n

Read a whole number `n` and print the value of

```
1 - 2 + 3 - 4 + 5 - 6 + ... (+ or -) n
```

Odd numbers are added and even numbers are subtracted. The last term is `+n` if `n` is odd and `-n` if `n` is even.

The catch: `n` can be as large as 10^18. A loop that runs `n` times would take thousands of years.
You need to find a pattern.

## Input

One line with the integer `n`.

## Output

One line with the value of the sum (an integer, possibly negative).

## Examples

| Input | Output | Why |
|---|---|---|
| `1` | `1` | just `1` |
| `4` | `-2` | `1 - 2 + 3 - 4` |
| `5` | `3` | `1 - 2 + 3 - 4 + 5` |
| `1000000000000000000` | `-500000000000000000` | find the pattern |

## Constraints

- `1 <= n <= 10^18`
- Your program must answer instantly (the tests allow 3 seconds).
- Use `input()` without a prompt message.

## Before you code

Do not start with code. Make a table by hand of `n` and the sum for `n = 1, 2, 3, ..., 8`.
Look at the even rows and the odd rows separately. Write the pattern you see as comments at the top of
`solution.py`, check it against a row you have not looked at yet, and only then write the program.
