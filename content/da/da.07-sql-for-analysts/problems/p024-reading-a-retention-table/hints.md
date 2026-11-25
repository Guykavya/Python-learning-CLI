## Hint 1

Take one cell, say Feb / M2 = 42. Which users does it describe, in which calendar month were they observed, and what is 42 a percentage of? Then ask why Mar / M2 cannot be filled in.

## Hint 2

```text
paragraph 1: row = signup month cohort, column = months since signup (M0 = signup month), empty cells = those months have not happened yet (immature, NULL not 0)
paragraph 2: compare cohorts only in the same column (M1: 60, 55, 62); newer cohorts have fewer observed months, so say "not yet known" for the rest
paragraph 3: pooled curve per column = sum of active users over cohorts that have that cell / sum of their sizes (weighted by size), cells that do not exist are not zeros
paragraph 4: raw counts depend on the cohort size (100, 120, 90, 150), percentages do not
```
