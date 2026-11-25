## Hint 1

How do you split the rows into "income missing" and "income present"? Which Boolean Series do you need, and how do you
select the other column with it? What does `mean` of an empty selection give?

## Hint 2

```text
m = df[col].isna()
missing_mean = df.loc[m, other].mean()
present_mean = df.loc[~m, other].mean()
gap = missing_mean - present_mean
return the three values as plain floats
```
