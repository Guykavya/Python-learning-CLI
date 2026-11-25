## Hint 1

Start from the margin formula and solve for `n`. What must you do with a fractional result, and in which direction?

## Hint 2

```text
z = stats.norm.ppf((1 + level) / 2)
n_for_margin: ceil((z * sd / margin) ** 2)
n_for_proportion: ceil(z * z * p * (1 - p) / margin ** 2)
```
