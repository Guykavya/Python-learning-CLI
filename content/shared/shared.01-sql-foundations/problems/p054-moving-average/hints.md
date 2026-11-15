## Hint 1

Which part of the window clause chooses *how many rows* to look at? What are the two ends of the frame for "this row and the two before"?

## Hint 2

```
SELECT day, amount,
       ROUND(AVG(amount) OVER (ORDER BY day ROWS BETWEEN <2> PRECEDING AND CURRENT ROW), 2) AS ma3
FROM daily
ORDER BY day
```
