# Print a month calendar

Read a year and a month and print that month as a calendar grid, with weeks starting on Monday.

**Rule:** do not import anything (no `calendar`, no `datetime`). Everything is computed by you.

## Input

Two lines: the year, then the month (1 = January, ..., 12 = December). Use `input()` without a
prompt message.

## Output

- The first line is exactly `Mo Tu We Th Fr Sa Su`.
- Then one line per week. Each day number is right-aligned in a width of 2 (` 1`, ` 9`, `10`), and
  cells are separated by **one** space. So every cell starts 3 characters after the previous one,
  exactly under its column heading.
- In the first week, the days before the 1st are blank cells (two spaces each, still separated by
  single spaces).
- The last week simply ends after the last day of the month.
- **No line has trailing spaces.**

## Examples

May 2024 (input `2024` then `5`) starts on a Wednesday:

```
Mo Tu We Th Fr Sa Su
       1  2  3  4  5
 6  7  8  9 10 11 12
13 14 15 16 17 18 19
20 21 22 23 24 25 26
27 28 29 30 31
```

The first week line is 7 spaces, then ` 1`: two blank cells (`  ` + ` ` + `  ` + ` `) and then ` 1`.

February 2021 (input `2021` then `2`) starts on a Monday and fills exactly 4 rows:

```
Mo Tu We Th Fr Sa Su
 1  2  3  4  5  6  7
 8  9 10 11 12 13 14
15 16 17 18 19 20 21
22 23 24 25 26 27 28
```

## Constraints

- 1583 <= year <= 9999 (Gregorian calendar)
- 1 <= month <= 12

## Plan it as sub-problems

This is a "build" problem: the skill being tested is breaking a bigger task into small ones that
you can solve and check one at a time. Suggested pieces:

1. **Is the year a leap year?** (divisible by 4, except centuries unless divisible by 400)
2. **How many days does the month have?** (31, 30, or 28/29 for February)
3. **On which weekday is the 1st?** Use Zeller's congruence. Treat January and February as months
   13 and 14 of the previous year; with `q` = 1 (the day), `m` the month, `K = year % 100`,
   `J = year // 100`:
   `h = (q + (13 * (m + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7`, where 0 = Saturday,
   1 = Sunday, 2 = Monday, ..., 6 = Friday. Convert it to "number of blank cells before the 1st"
   (0 for Monday, 6 for Sunday).
4. **Print the grid**: walk through the cells, keep a column counter, and print a line every 7 cells.

Write these four steps as comments at the top of `solution.py` and finish and test each one
(print intermediate values!) before starting the next.
