## Hint 1

For each predictor in turn, which columns are the response and which are the explanatory variables? What do you do if there is only one predictor?

## Hint 2

```text
for each name:
    others = predictors without name
    r2 = OLS(df[name], add_constant(df[others])).fit().rsquared
    vif[name] = 1 / (1 - r2)
return Series(vif).sort_values(descending)
```
With a single predictor there are no others; its VIF is 1.
