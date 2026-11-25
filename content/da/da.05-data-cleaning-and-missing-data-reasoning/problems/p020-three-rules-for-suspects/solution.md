## Approach

All three rules have the same shape: **a centre, a spread, and a limit**. IQR uses the quartiles (a middle chunk of the data
and its width), z uses the mean and the standard deviation, robust z uses the median and the MAD. The difference is how
much one extreme value can move the centre and the spread: a lot for mean and std, hardly at all for median and MAD. That
is the masking effect the chapter shows. Each function returns a Boolean *flag*, not a cleaned Series, because the rule is
"flag before you delete".

Edge cases come out of the arithmetic or need one line: a missing value compares as `False`; a constant column has std 0
(`0/0 = NaN`, `NaN > t` is `False`) and IQR 0 (both fences equal the constant); for the MAD of 0 we return all `False`.

## Code

```python
import pandas as pd


def flag_iqr(x, k=1.5):
    q1, q3 = x.quantile([0.25, 0.75])
    spread = q3 - q1
    return (x < q1 - k * spread) | (x > q3 + k * spread)


def flag_z(x, t=3):
    return ((x - x.mean()) / x.std()).abs() > t


def flag_mad(x, t=3.5):
    med = x.median()
    mad = (x - med).abs().median()
    if pd.isna(mad) or mad == 0:
        return pd.Series(False, index=x.index)
    return (0.6745 * (x - med) / mad).abs() > t
```

## Complexity

O(n log n) in the worst case (quantiles and medians need sorting); the flags are O(n).

## Another way

Compare on **known** data, as the chapter does, before you trust a rule: plant errors in a clean Series and count how many
each rule finds and how many honest values it flags. For skewed variables such as income, apply the rule to `np.log10(x)`
(a mistake of 100 times is an addition of 2 on the log scale). And write the final rule down as a domain rule ("monthly
income above 1,000,000 is not credible"): easier to explain and audit.
