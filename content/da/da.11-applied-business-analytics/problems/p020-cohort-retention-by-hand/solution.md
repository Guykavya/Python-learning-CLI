## Approach

- Cohort 0 (a, b): months 0, 1, 2, 3 -> 2/2, 1/2, 0/2, 1/2.
- Cohort 1 (c, d): months 1, 2, 3 -> 2/2, 1/2 (c), 1/2 (d); month 4 does not exist.
- Cohort 2 (e): months 2 and 3 -> 1/1, 1/1.
- Cohort 3 (f): month 3 -> 1/1.

## Code

```text
0 2 1.00 0.50 0.00 0.50
1 2 1.00 0.50 0.50 -
2 1 1.00 1.00 - -
3 1 1.00 - - -
```

## Complexity

Not applicable (a trace problem).

## Another way

With `pd.crosstab` the same matrix is two lines; doing it once by hand shows why the lower-right triangle is empty by construction.
