## Approach

The overall rate is `sum(share x rate)`. Its change splits exactly into a share part and a rate part when each is weighted by the **average** of the other. pandas aligns the four Series by segment, so the arithmetic is the formula itself.

## Code

```python
import pandas as pd


def mix_rate_decomposition(o, dim, before, after):
    def period(p):
        return o[o["month"].between(pd.Period(p[0], "M"), pd.Period(p[1], "M"))]

    b, a = period(before), period(after)
    sb, sa = b[dim].value_counts(normalize=True), a[dim].value_counts(normalize=True)
    missing = sorted(set(sb.index) ^ set(sa.index))
    if missing:
        raise ValueError(f"segment missing in one period: {missing[0]}")
    rb, ra = b.groupby(dim)["churned"].mean(), a.groupby(dim)["churned"].mean()
    mix = float(((sa - sb) * (rb + ra) / 2).sum()) * 100
    rate = float(((ra - rb) * (sa + sb) / 2).sum()) * 100
    total = float(a["churned"].mean() - b["churned"].mean()) * 100
    return mix, rate, total
```

## Complexity

O(n).

## Another way

Shapley-style decompositions extend the idea to more than two factors (mix by two dimensions at once); for one dimension they reduce to these averaged weights.
