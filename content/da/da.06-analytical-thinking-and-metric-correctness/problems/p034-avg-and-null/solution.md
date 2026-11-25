## Approach

`GROUP BY technician`, then two aggregates over `rating`: `COUNT(rating)` counts only non-NULL ratings and
`AVG(rating)` divides by that same count, so both skip the visits that nobody rated. A group with no ratings has
`COUNT = 0` and `AVG = NULL`: "unknown", which is the honest answer.

## Code

```python
QUERY = """
SELECT technician,
       COUNT(rating)          AS rated,
       ROUND(AVG(rating), 2)  AS avg_rating
FROM visits
GROUP BY technician
ORDER BY technician
"""
```

## Complexity

One pass over `visits`: O(n) with one running sum and count per technician.

## Another way

`ROUND(SUM(rating) * 1.0 / COUNT(rating), 2)` is the same calculation spelled out (a `NULL` appears when `COUNT` is 0
in some engines; SQLite divides by zero to `NULL`). Show `rated` next to the average, as chapter 7.4 asks for rates:
an average of one rating and an average of 200 ratings are not equally trustworthy.
