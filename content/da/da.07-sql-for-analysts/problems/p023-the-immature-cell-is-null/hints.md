## Hint 1

How many cells does the grid have, and which CTE can produce all combinations of cohorts and the numbers 0 to 5? Which condition decides whether a cell is observed? Then, which join gives a count (or nothing) for each cell, and where should the zero come from, and where must it **not** come from?

## Hint 2

```text
size  : cohort, cohort_size
grid  : size CROSS JOIN generate_series(0, 5) AS g(k)
cnt   : (cohort, k) -> distinct active users  (complete months only)
final : grid LEFT JOIN cnt;  CASE WHEN cohort + to_months(k) < DATE '2025-07-01' THEN COALESCE(cnt.active, 0) END AS active_users
```

The `CASE` without `ELSE` returns `NULL` for immature cells; `COALESCE` is applied only inside the observed branch.
