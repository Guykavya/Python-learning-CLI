## Hint 1

What are the two things `het_breuschpagan` needs? It returns four numbers: which one is the p-value of the LM test, and which is the F-test's?

## Hint 2

```text
lm, lm_p, f, f_p = het_breuschpagan(resid, result.model.exog)
bp_p = lm_p
se_robust = result.get_robustcov_results(cov_type="HC3").bse
```
