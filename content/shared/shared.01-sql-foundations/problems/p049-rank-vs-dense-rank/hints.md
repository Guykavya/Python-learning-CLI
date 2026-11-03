## Hint 1

You need two window functions in the same `SELECT`. Do they have to use the same `OVER (...)` clause? What should that clause sort by?

## Hint 2

```
SELECT name, salary,
       RANK()       OVER (ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS drnk
FROM employees
ORDER BY salary DESC, name
```

Notice that no name tie-break is needed inside the window: ties are meant to share a rank.
