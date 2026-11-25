## Hint 1

Count the variables in the facts: store, quarter, revenue. In the wide table, where is "quarter" stored: in a column,
or in the column **names**? What must code do to group by something hidden in column names?

## Hint 2

```text
1. tidy: each variable a column, each observation a row -> groupby("quarter") is one line
2. wide: for people (reports, a grid to read), some models/spreadsheets
3. (a) long (the library maps columns to x / colour)  (b) wide  (c) long  (d) long + groupby
4. melt (wide -> long), pivot / pivot_table (long -> wide); check shape = stores x quarters, totals equal
```
Write a short paragraph for each numbered question.
