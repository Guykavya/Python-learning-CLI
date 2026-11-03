## Hint 1

Write the full result of each query **without** DISTINCT first, then cross out rows that repeat an earlier row. For query 2, what counts as "the same row": the same category only, or the same pair?

## Hint 2

```
Q1: one column  -> unique categories
Q2: two columns -> unique (category, author_id) pairs
Q3: price >= 15 is 1 or 0 for each row -> only two possible values
Q4: unique prices; 9.99 and 18.0 each appear twice in the table
```

`DESC` in query 4 means largest first.
