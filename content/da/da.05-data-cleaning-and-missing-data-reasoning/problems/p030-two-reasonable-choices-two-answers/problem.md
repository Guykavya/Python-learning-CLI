# Two reasonable choices, two answers

Chapter sections 9.1, 9.2 and 9.6. The most important habit of the module: **do not pick one way to handle missing
values and report one number.** Compute the answer two defensible ways, show both, and measure the gap.

You get a table of customers with `city`, `age` and `income` (`income` has missing values, `age` and `city` do not).
Write `two_ways(df)`, which returns a dict with three entries:

- `"complete"`: a Series, the **mean income per city** using only the rows where income is present (complete cases);
- `"filled"`: a Series, the **mean income per city** after every missing income is filled with the **median of the
  observed incomes in the same age band**;
- `"max_diff"`: a `float`, the **largest absolute difference** between the two Series over the cities.

Details:

- Age bands: `age < 30`, `30 <= age < 45`, `age >= 45`. The median of a band uses the **observed** incomes of that
  band only (not the filled ones).
- Both Series have the city names as the index, sorted, and the name `"income"`.
- If a band has no observed income at all, the rows of that band stay missing (and are skipped by the mean).
- Do not change `df`.

Why age? In the tests, young people earn less **and** skip the income question more often (this is MAR: missingness
depends on a visible column). Dropping those rows then makes the average look too high, and filling by age band
repairs part of it. The tests check that the two answers really differ, and that each one matches a slow, obvious
computation.

## Example

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"city":   list("XXXYYY"),
                   "age":    [25, 25, 50, 25, 35, 50],
                   "income": [100, np.nan, 300, np.nan, 200, 400]})
r = two_ways(df)
print(r["complete"].to_dict())
print({k: round(v, 2) for k, v in r["filled"].to_dict().items()})
print(round(r["max_diff"], 2))
```

```text
{'X': 200.0, 'Y': 300.0}
{'X': 166.67, 'Y': 233.33}
66.67
```

The band medians of the observed incomes are 100 (under 30), 200 (30 to 44) and 350 (45 and over). City X: rows
`100, 100 (filled), 300` have mean 166.67; city Y: `100 (filled), 200, 400` have mean 233.33.
