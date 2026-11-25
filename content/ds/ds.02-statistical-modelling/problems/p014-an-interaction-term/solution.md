## Approach

The coefficient of `experience` is the slope for the baseline level. Add each interaction coefficient to it to get the other slopes.

## Code

```python
import numpy as np  # patsy looks up `np` here, in the file that calls ols()
import statsmodels.formula.api as smf


def experience_slope_by_education(df):
    formula = ("np.log(wage) ~ experience * C(education, Treatment(reference='school'))"
               " + C(city)")
    res = smf.ols(formula, data=df).fit()
    base = float(res.params["experience"])
    slopes = {"school": base}
    for name, value in res.params.items():
        if name.startswith("experience:") and "[T." in name:
            level = name.split("[T.")[1].rstrip("]")
            slopes[level] = base + float(value)
    return slopes
```

## Complexity

O(n p^2).

## Another way

Fit a separate regression for each education group and read each slope. The interaction model uses all rows for the shared parts (such as the city effects) and tests the differences directly.
