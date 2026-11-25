## Hint 1

Which rows does "complete cases" use, and what does a plain `groupby("city")["income"].mean()` already do with missing
values? How do you give every row an age band (which function cuts numbers into intervals, and are the bounds
open or closed on the left)? Which groupby method puts a **group statistic on every row** so that it can fill the gaps?

## Hint 2

```text
complete = df.groupby("city")["income"].mean()                 # mean skips missing values
band = cut(df.age, [-inf, 30, 45, inf], right=False)           # [-inf,30), [30,45), [45,inf)
med = df.groupby(band)["income"].transform("median")           # median of OBSERVED incomes of the band, on every row
filled_income = df["income"].fillna(med)
filled = filled_income.groupby(df["city"]).mean()
max_diff = float((filled - complete).abs().max())              # name both Series "income"
```
