# The k-th digit of 123456789101112...

Write all positive integers one after another, with nothing between them:

```
123456789101112131415161718192021...
```

Read `k` and print the `k`-th digit of this endless sequence (the first digit is digit 1).

**Rules:**

- Use arithmetic only: no `str()`, no f-strings, no `repr()` or `format()`.
- `k` can be as large as 10^18, so you cannot walk through the sequence digit by digit or number
  by number. You must jump.

## Input

One line: the integer `k`. Use `input()` without a prompt message.

## Output

One line: a single digit (0 to 9).

## Examples

| k | Output | Why |
|---|---|---|
| `1` | `1` | the sequence starts with 1 |
| `9` | `9` | the last one-digit number |
| `10` | `1` | the first digit of 10 |
| `11` | `0` | the second digit of 10 |
| `12` | `1` | the first digit of 11 |
| `189` | `9` | the last digit of 99 |
| `190` | `1` | the first digit of 100 |
| `192` | `0` | the last digit of 100 |

## Constraints

- 1 <= k <= 10^18
- Time limit: 3 seconds.

## Before you code

Plan on paper first, in three steps, and write them as comments at the top of `solution.py`:

1. How many digits do all the 1-digit numbers use together? All 2-digit numbers? All 3-digit numbers?
   Which block does `k` fall into?
2. Inside that block, which number contains the `k`-th digit?
3. Which digit of that number is it, and how do you pull it out with `//` and `%`?

Check your plan by hand on `k = 11` and `k = 190`.
