## Approach

Two separate jobs, done in order.

1. **Validate.** Compute `leap` with the 4/100/400 rule. Reject months outside 1..12. Use if/elif to
   get the length of the month (31, 30, or 28/29 for February). Reject days outside `1..length`.
2. **Weekday.** Zeller's congruence counts days in a clever way: putting January and February at the
   *end* of the previous year means the leap day (29 February) is the last day of a "year", so the
   leap-year corrections `K // 4`, `J // 4` and `5 * J` work without special cases.
   `(13 * (m + 1)) // 5` adds up the uneven month lengths. The result `h` (0..6) is turned into a name
   with an if/elif chain.

## Trace

Input `1`, `1`, `2000`:

| step | m | y | K | J | h |
|---|---|---|---|---|---|
| start | 1 | 2000 | | | |
| move Jan | 13 | 1999 | | | |
| split year | 13 | 1999 | 99 | 19 | |
| formula | 13 | 1999 | 99 | 19 | (1 + 36 + 99 + 24 + 4 + 95) % 7 = 259 % 7 = 0 |

`h = 0` means Saturday.

## Code

```python
day = int(input())
month = int(input())
year = int(input())

leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

if month < 1 or month > 12:
    print("invalid date")
else:
    if month == 2:
        if leap:
            length = 29
        else:
            length = 28
    elif month == 4 or month == 6 or month == 9 or month == 11:
        length = 30
    else:
        length = 31

    if day < 1 or day > length:
        print("invalid date")
    else:
        # Zeller: January and February count as months 13 and 14 of the previous year.
        m = month
        y = year
        if m < 3:
            m += 12
            y -= 1
        k = y % 100
        j = y // 100
        h = (day + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
        if h == 0:
            print("Saturday")
        elif h == 1:
            print("Sunday")
        elif h == 2:
            print("Monday")
        elif h == 3:
            print("Tuesday")
        elif h == 4:
            print("Wednesday")
        elif h == 5:
            print("Thursday")
        else:
            print("Friday")
```

## Complexity

A fixed number of operations whatever the date: O(1) time and O(1) memory.

## Another way

**Count days from a known date.** You know 1 January 2000 was a Saturday. Count the days between that
date and the target (add 365 or 366 for each whole year, then the lengths of the whole months, then
the day) and take the count `% 7`. This is easier to understand and to check, but it needs a loop over
years, and you must handle dates before 2000 carefully (counting backwards). Prefer it when you cannot
remember the formula; prefer Zeller when you want a constant-time answer.

## Edge cases

- 29 February: valid only in leap years. 2000 yes, 1900 no, 2024 yes, 2023 no.
- Day 0, negative days, month 0, month 13: all invalid.
- January 1583: Zeller uses year 1582 internally, which is fine because it is only arithmetic.
