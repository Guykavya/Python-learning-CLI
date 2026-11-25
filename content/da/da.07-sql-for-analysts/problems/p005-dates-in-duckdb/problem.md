# Dates in DuckDB

Chapter sections 2.2 and 2.4. Date arithmetic has rules that surprise people: weeks start on a Monday, a month plus one month
clips to the end of a shorter month, `date_diff` counts **boundaries crossed** and not elapsed time, and `/` does not divide
like Python's `//`. The helper `one` returns the first value of a query and prints dates as `YYYY-MM-DD`.

```python
import duckdb

con = duckdb.connect()


def one(sql):
    value = con.execute(sql).fetchall()[0][0]
    return value.strftime("%Y-%m-%d") if hasattr(value, "strftime") else value


print(one("SELECT date_trunc('week', DATE '2025-01-01')"))
print(one("SELECT dayname(DATE '2025-01-01')"))
print(one("SELECT DATE '2025-03-31' + INTERVAL 1 MONTH"))
print(one("SELECT date_diff('month', DATE '2025-01-31', DATE '2025-02-01')"))
print(one("SELECT date_diff('month', DATE '2025-01-01', DATE '2025-01-31')"))
print(one("SELECT date_diff('day', DATE '2025-01-31', DATE '2025-03-01')"))
print(one("SELECT date_trunc('month', TIMESTAMP '2025-02-28 23:59:59')"))
print(one("SELECT 7 / 2"), one("SELECT 7 // 2"))
print(one("SELECT 1 / 0"), one("SELECT NULLIF(0, 0)"))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Write a missing value (SQL `NULL`) as
`None`, and a number as Python prints it.

Do not run the code before you have written your answer.

## Example

For `one("SELECT date_trunc('month', DATE '2025-05-17')")` the program would print `2025-05-01`, and for
`one("SELECT 9 // 2")` it would print `4`.

## After you answer

- 1 January 2025 is a Wednesday. Which Monday is the start of its week, and why is it in the previous year?
- `date_diff('month', ...)` gives 1 for two dates one day apart and 0 for two dates thirty days apart. What does it count?
- Why is `1 / 0` a better reason to use `NULLIF` than "avoiding an error"?
