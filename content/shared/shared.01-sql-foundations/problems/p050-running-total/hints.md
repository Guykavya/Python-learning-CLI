## Hint 1

Which function adds numbers up? And which part of `OVER (...)` makes the sum restart for each store, and which part decides the order of accumulation?

## Hint 2

```
SELECT store, day, amount,
       SUM(amount) OVER (PARTITION BY <store> ORDER BY <day>) AS running
FROM daily_sales
ORDER BY store, day
```

With `ORDER BY` inside `OVER` and no frame given, the default frame is "from the first row to the current row".
