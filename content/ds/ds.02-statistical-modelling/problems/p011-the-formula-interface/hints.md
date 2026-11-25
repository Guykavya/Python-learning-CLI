## Hint 1

How do you ask a formula for a log of the response? And how do you make a column categorical with a named baseline? Look at section 6.3.

## Hint 2

```text
formula = "np.log(wage) ~ experience + C(education, Treatment(reference='school')) + C(city)"
return smf.ols(formula, data=df).fit()
```
