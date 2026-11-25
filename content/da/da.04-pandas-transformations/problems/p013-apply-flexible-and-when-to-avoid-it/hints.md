## Hint 1

Count the Python function calls each line makes when there are 5,000 groups. Which built-in method gives a group
total, which one puts a group statistic on every row, and which pair of methods takes the first N rows of each group
after sorting?

## Hint 2

```text
1. apply: sub-table per group -> Python call -> glue results; overhead x number of groups
2. sum -> groupby(...)["revenue"].sum()
   z-score -> (x - g.transform("mean")) / g.transform("std")
   top 2 -> sort_values(..., ascending=False).groupby(...).head(2)
3. pandas 3: grouping columns excluded -> KeyError; use d.name
4. apply when logic cannot be vectorised; measure before and after; same result?
```
Write a short paragraph for each numbered question.
