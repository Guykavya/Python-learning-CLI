## Approach

Split by `isna()` of the column, take the mean of the other column in each part, subtract. An empty part gives `NaN`
from `mean`, which is the required answer. The value of the function is in how you read it: in the tests, hiding
incomes of people under 40 more often gives an `age` gap of about -5 years, but **no** gap in `edu_years`, which has
nothing to do with the hiding. A gap tells you which visible column the missingness is linked to, nothing more.

## Code

```python
def missingness_gap(df, col, other):
    m = df[col].isna()
    missing_mean = float(df.loc[m, other].mean())
    present_mean = float(df.loc[~m, other].mean())
    return {"missing_mean": missing_mean, "present_mean": present_mean, "gap": missing_mean - present_mean}
```

## Complexity

O(n): one mask, two means.

## Another way

For a categorical `other`, compare the **share of missing values** per category (problem p026). For many columns at
once, loop over the columns and sort by the absolute gap divided by the standard deviation of the column, so that
columns with different units can be compared.

Remember the limit from the chapter: this finds links to **visible** columns (MAR). It cannot tell MAR from MNAR,
because MNAR depends on the hidden value itself, and data alone cannot show that.
