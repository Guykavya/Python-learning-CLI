## Model answer

1. At **12 rows** the model **overfits severely**: training RMSE is 0.145 (below the noise floor of 0.30, so it has fitted the noise) but validation RMSE is 78.9, hundreds of times larger. A degree-12 polynomial has 13 parameters for 12 points; it can pass through every point and swings wildly between them, so it is terrible on new points. The gap (78.8) is huge.
2. As `n_train` grows the **validation error falls** (78.9 -> 7.4 -> 0.43 -> 0.33 -> 0.31), the **training error rises** (0.145 -> 0.289) and the **gap shrinks** (78.8 -> 0.019). The training error rises because with more rows the model can no longer pass through every point: it is forced to average over the noise and learn the shape instead.
3. From about **40-80 rows** the model is usable (gap 0.17 at 40, 0.06 at 80). At 320 rows both errors are near the noise floor (0.29 and 0.31, floor 0.30) and the gap is only 0.019: the model no longer overfits at that size; the flexibility is now supported by enough data.
4. Without more data: **regularise** (ridge or lasso penalty on the coefficients), **lower the degree** (a simpler model), use **fewer features**, or **average** several models. All of them reduce variance.
5. An underfitting (high-bias) curve has a **small gap** and **both errors high and flat** (about 0.51 and 0.53 for the line at 320 rows); the curves converge at a poor level, so more data do not help. The overfitting curve has a **large gap that narrows** and low training error.

**Checklist: your answer should mention**
- [ ] low training error with a much higher validation error means overfitting (a large gap)
- [ ] the gap narrows as the training set grows, because variance falls with n
- [ ] the training error rises with n because the model can no longer memorise
- [ ] both errors end near the noise floor when the data are enough
- [ ] remedies: more data, a simpler model, regularisation, fewer features
- [ ] contrast with underfitting: small gap, both errors high and flat, more data do not help
