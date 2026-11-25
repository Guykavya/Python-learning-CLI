## Hint 1

Which of the three counts must ignore `NULL`, and which one must not? What is the difference between `COUNT(*)` and
`COUNT(method)`? How do you count different values of one column only?

## Hint 2

```text
SELECT COUNT(*)                    AS rows,
       COUNT(method)               AS with_method,
       COUNT(DISTINCT customer_id) AS distinct_customers
FROM payments
```
