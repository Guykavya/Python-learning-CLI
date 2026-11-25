## Hint 1

Which argument of `sm.GLM` or `smf.glm` takes an offset? What function of the exposure do you pass: the exposure itself or its logarithm?

## Hint 2

```text
model = smf.glm("count ~ treated", data=df, family=Poisson(), offset=log(df["exposure"]))
res = model.fit()
b = res.params["treated"]; lo, hi = res.conf_int().loc["treated"]
return exp(b), exp(lo), exp(hi)
```
