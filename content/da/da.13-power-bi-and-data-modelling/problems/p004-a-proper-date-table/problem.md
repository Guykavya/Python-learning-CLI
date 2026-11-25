# A proper date table

Chapter section 3.4. Every model needs a **date table**: one row per day with **no gaps**, covering **all the dates of the facts**. Time intelligence (same period last year, year to date) only works on a complete calendar. Power BI cannot run offline; this problem is about the model and its numbers, which we build and check in pandas.

Write `date_table(start, end)` returning a DataFrame with **one row per day from `start` to `end` inclusive** and these columns, in this order:

| column | content |
|---|---|
| `DateKey` | the integer `yyyymmdd` |
| `Date` | the date (a `Timestamp`) |
| `Year` | the year (int) |
| `Quarter` | `"Q1"` to `"Q4"` |
| `MonthNum` | 1 to 12 |
| `MonthName` | three letters: `"Jan"`, ..., `"Dec"` |
| `YearMonth` | `"2024-03"` |

`start` and `end` can be dates, strings or timestamps. If `end` is before `start`, raise `ValueError("end is before start")`.

## Example

`date_table("2024-02-27", "2024-03-02")` has 5 rows (2024 is a leap year: 27, 28, 29 February, 1 and 2 March), the first `DateKey` is `20240227`.
