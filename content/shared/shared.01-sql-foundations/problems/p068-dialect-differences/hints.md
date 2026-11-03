## Hint 1

Go through the query clause by clause: the date function, the `||` operator, `LIKE`, the division, `GROUP BY` with columns that are not grouped, `ORDER BY` on a column with NULLs, and `LIMIT`. For each one ask: is it standard SQL, or something SQLite does its own way?

## Hint 2

Think about two classes of problems: "the other database refuses with an error" (you notice immediately) and "the other database accepts it but gives a different answer" (you may notice months later). Examples of the second class: integer division, case sensitivity of `LIKE`, where NULLs sort, and what `||` means in MySQL by default.
