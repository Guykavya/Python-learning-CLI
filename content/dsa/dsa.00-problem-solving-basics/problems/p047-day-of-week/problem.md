# Day of the week for any date

Read a date as three numbers: the day, then the month, then the year. First decide whether
the date actually exists. If it does, print the day of the week it falls on.

**Rule:** do not import anything (no `datetime`, no `calendar`). Work it out with arithmetic.

A date exists when:

- the month is between 1 and 12, and
- the day is between 1 and the number of days in that month.

Months 1, 3, 5, 7, 8, 10, 12 have 31 days. Months 4, 6, 9, 11 have 30 days. February has 29 days
in a leap year and 28 otherwise. A year is a leap year when it is divisible by 4, except years
divisible by 100, which are leap years only when also divisible by 400 (so 2000 is a leap year,
1900 is not).

To find the weekday, use **Zeller's congruence**. Treat January and February as months 13 and 14
of the *previous* year. Then, with `q` = day, `m` = month (3..14), `K` = year % 100 and
`J` = year // 100 (using the adjusted year):

```
h = (q + (13 * (m + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7
```

`h` is 0 for Saturday, 1 for Sunday, 2 for Monday, ..., 6 for Friday.

## Input

Three lines: the day, the month, the year. Each is an integer. Use `input()` without a prompt message.

## Output

One line: either the exact text `invalid date`, or the weekday name with a capital first letter:
`Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday` or `Sunday`.

## Examples

| Input (day, month, year) | Output | Why |
|---|---|---|
| `1`, `1`, `2000` | `Saturday` | |
| `29`, `2`, `2024` | `Thursday` | 2024 is a leap year |
| `29`, `2`, `2023` | `invalid date` | 2023 is not a leap year |
| `29`, `2`, `1900` | `invalid date` | 1900 is divisible by 100 but not by 400 |
| `31`, `4`, `2024` | `invalid date` | April has 30 days |
| `0`, `5`, `2024` | `invalid date` | there is no day 0 |

## Constraints

- 1583 <= year <= 9999 (the Gregorian calendar).
- day and month can be any integers (including 0 and negatives); you must reject impossible ones.

## Before you code

Split it into two separate jobs: (1) is the date valid? (2) which weekday? Write both plans as
comments at the top of `solution.py`. Check your formula by hand on 1 1 2000 before typing it.
