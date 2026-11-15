## Hint 1

A: which function gives a part of a text, and which one counts characters? For the year, which function takes a format string? B: can you reuse the year expression in `WHERE`? C: how do you subtract two dates in SQLite: as text, or as numbers?

## Hint 2

```
A: strftime('%Y', published) AS year, substr(title, 1, 3) AS short, length(title) AS len
B: WHERE strftime('%Y', published) = '2022'     -- compare TEXT with TEXT
C: CAST(julianday('2024-01-01') - julianday(published) AS INTEGER) AS days_old
```
