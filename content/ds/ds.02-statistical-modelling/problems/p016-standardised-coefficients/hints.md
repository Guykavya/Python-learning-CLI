## Hint 1

Which columns need a z-score? Does the response need one too? What happens to the intercept after you centre everything?

## Hint 2

```text
z = (df[cols] - df[cols].mean()) / df[cols].std()
fit sm.OLS(z[y], sm.add_constant(z[xs]))
return params without 'const'
```
