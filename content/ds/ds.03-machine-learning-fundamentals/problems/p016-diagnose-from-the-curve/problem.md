# Diagnose from the curve

Chapter sections 7 and 14. From the **last row** of a learning curve you can say what is wrong. Rules (the chapter's rule with a bias check added):

```text
error      = validation               (regression; an error already)
           = 1 - validation           (classification; validation is an accuracy)
rel_gap    = gap / max(abs(error), 1e-12)
if rel_gap > 0.15                       -> "high variance"
elif floor is given and error > 1.25 * floor -> "high bias"
else                                    -> "fine"
```

Write `diagnose(lc, task="regression", floor=None)`. `lc` is a DataFrame with the columns `n_train, train, validation, gap` (as in the previous problem). Use only its **last row**. `floor` is the best error you could hope for (the noise floor); without it a small gap is called `fine`. For any other `task` raise `ValueError`.

## Example

```text
last row: train 0.05, validation 0.90, gap 0.85          -> "high variance"
last row: train 0.50, validation 0.53, gap 0.03, floor 0.30 -> "high bias"
last row: train 0.29, validation 0.31, gap 0.02, floor 0.30 -> "fine"
```
