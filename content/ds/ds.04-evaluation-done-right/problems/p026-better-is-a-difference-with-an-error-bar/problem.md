# Better is a difference with an error bar

Chapter section 8.4. "Model A has AUC 0.78, model B 0.76" says nothing until you know how much such a difference moves between samples. Both models were scored on the **same** test rows, so resample the rows **once** and score both on each resample: a **paired bootstrap**.

Write `paired_difference(y, p_model, p_base, reps=500, seed=0)` returning `(mean_diff, lo, hi)`:

- use one `rng = np.random.default_rng(seed)`; in each repetition draw `idx = rng.integers(0, n, n)`
- skip a resample that contains only one class (AUC undefined)
- record `roc_auc_score(y[idx], p_model[idx]) - roc_auc_score(y[idx], p_base[idx])`
- return the mean of the recorded differences and their 2.5th and 97.5th percentiles (`np.percentile`), as floats

## Example

```text
a genuinely better model:   (0.05, 0.03, 0.07)    -> the interval excludes 0: better
two equivalent models:      (0.00, -0.01, 0.01)   -> includes 0: no evidence
```
