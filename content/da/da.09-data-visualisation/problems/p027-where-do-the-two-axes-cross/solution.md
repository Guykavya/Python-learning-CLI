## Approach

`l` is the same for the first three cases with left limits (0, 50): `0.80, 0.84, 0.88, 0.92`. For the fourth, left limits (0, 100) give `0.40, 0.42, 0.44, 0.46`.

- right (0, 50): `r = 0.60, 0.68, 0.76, 0.84` -> `l > r` in all 4 months.
- right (0, 40): `r = 0.75, 0.85, 0.95, 1.05` -> only the first month (0.80 > 0.75) -> 1.
- right (20, 40): the divisor is `40 - 20 = 20`, so `r = (30-20)/20, (34-20)/20, (38-20)/20, (42-20)/20 = 0.50, 0.70, 0.90, 1.10` -> `l > r` in the first two months (0.80 > 0.50 and 0.84 > 0.70) -> 2.
- left (0, 100), right (0, 40): `l = 0.40...0.46`, `r = 0.75...1.05` -> never -> 0.

## Code

```text
(0, 50) (0, 50) 4 of 4
(0, 50) (0, 40) 1 of 4
(0, 50) (20, 40) 2 of 4
(0, 100) (0, 40) 0 of 4
```

## Complexity

Not applicable (a trace problem).

## Another way

Put both lines on **one** axis (they share a unit), or plot each series as an index (divided by its first value). Then "which is higher" cannot depend on a choice of limits.
