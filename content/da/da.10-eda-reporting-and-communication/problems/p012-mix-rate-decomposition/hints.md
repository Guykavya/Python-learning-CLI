## Hint 1

You need four Series indexed by segment: share before, share after, rate before, rate after. With them, both effects are one line each of vectorised arithmetic followed by `.sum()`.

## Hint 2

```text
b, a = rows of each period
sb, sa = b[dim].value_counts(normalize=True), a[dim].value_counts(normalize=True)
rb, ra = b.groupby(dim)["churned"].mean(), a.groupby(dim)["churned"].mean()
check that sb and sa have the same segments
mix = ((sa - sb) * (rb + ra) / 2).sum() * 100
rate = ((ra - rb) * (sa + sb) / 2).sum() * 100
```
