## Hint 1

Does `sm.OLS(df['y'], df[['x']])` have an intercept? What does `sm.add_constant` do to a DataFrame?

## Hint 2

```text
X = sm.add_constant(df[xs])
return sm.OLS(df[y], X).fit()
```
