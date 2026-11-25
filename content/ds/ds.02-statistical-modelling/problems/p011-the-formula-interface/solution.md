## Approach

Put the transformation and the categorical coding inside the formula, so predictions and reports keep working on raw columns.

## Code

```python
import numpy as np  # patsy looks up `np` here, in the file that calls ols()
import statsmodels.formula.api as smf


def fit_wages(df):
    formula = ("np.log(wage) ~ experience"
               " + C(education, Treatment(reference='school'))"
               " + C(city)")
    return smf.ols(formula, data=df).fit()
```

## Complexity

O(n p^2).

## Another way

Create `log_wage` and a categorical column with `pd.Categorical(..., categories=[...])` first. The formula version keeps the transformation attached to the model, which avoids train/predict mismatches.
