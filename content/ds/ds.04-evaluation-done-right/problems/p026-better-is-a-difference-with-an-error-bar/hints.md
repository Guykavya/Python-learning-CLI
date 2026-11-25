## Hint 1

Why resample the **same** rows for both models instead of bootstrapping each model separately? What happens to the noise that both models share?

## Hint 2

```text
rng = default_rng(seed); diffs = []
repeat reps: idx = rng.integers(0, n, n)
    if y[idx] has one class: continue
    diffs.append(auc(y[idx], p_model[idx]) - auc(y[idx], p_base[idx]))
return mean(diffs), percentile(diffs, 2.5), percentile(diffs, 97.5)
```
