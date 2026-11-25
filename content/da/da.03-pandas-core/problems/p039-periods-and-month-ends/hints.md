## Hint 1

`to_period("M")` keeps only the year and month; `astype(str)` shows it as `YYYY-MM`. Which of the three dates are in which month? Nothing is rounded to a month end here.

## Hint 2

Ask of each offset: "What is the *first month end I land on*?"
`MonthEnd(1)` always moves to a month end **strictly after** a date that is already a month end, and to the end of the same month for any other date.
`MonthEnd(0)` stays put on a month end, and otherwise rolls forward to the end of the same month.
`DateOffset(months=1)` moves the month number by one and keeps the day, but clips it to the last valid day.

```text
31 Jan + 1 month   -> day 31 does not exist in February -> last day of February
31 Jan + MonthEnd(1) -> already a month end, so the NEXT one
31 Jan + MonthEnd(0) -> already a month end, stay
15 Jan + MonthEnd(1) or (0) -> 31 Jan
```
`days_in_month` of a February: 29 in a leap year (divisible by 4, but a century year only if divisible by 400).
