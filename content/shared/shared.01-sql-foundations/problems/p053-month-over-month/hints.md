## Hint 1

Which window function gives you a value from the row before? What does it return when there is no row before, and which clause says what "before" means?

## Hint 2

```
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY <month>) AS change
FROM monthly_sales
ORDER BY month
```

NULL minus a number is NULL, which is exactly what you want for the first month.
