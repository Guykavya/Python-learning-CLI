## Hint 1

What does `AVG` do with a `NULL`? Which count counts only the non-NULL values of a column? What does `AVG` return for a
group in which every value is `NULL`, and is that the number you want to show?

## Hint 2

```text
SELECT technician,
       COUNT(rating)         AS rated,          -- non-NULL only
       ROUND(AVG(rating), 2) AS avg_rating      -- skips NULL; NULL if nothing to average
FROM visits GROUP BY technician ORDER BY technician
```
