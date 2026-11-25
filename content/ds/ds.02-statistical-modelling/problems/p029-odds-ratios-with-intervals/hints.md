## Hint 1

Which attributes hold the coefficients, their interval and their p-values? Which of them should be exponentiated?

## Hint 2

```text
ci = conf_int()   # on the log-odds scale
table = DataFrame({"odds_ratio": exp(params), "ci_low": exp(ci[0]), "ci_high": exp(ci[1]), "p": pvalues})
return table.round(3)
```
