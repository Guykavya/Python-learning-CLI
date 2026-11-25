# Beat the baseline?

Chapter section 3. A model is only useful if it does better than the baseline on data it has not seen. Write

```text
beats_baseline(model, X_tr, y_tr, X_te, y_te, task)   ->   (model_score, baseline_score, beats)
```

- Fit `model` on the training data (it arrives **unfitted**).
- **Regression**: the score is the **RMSE** on the test data (lower is better). The baseline predicts the training mean. `beats` is `True` only if the model's RMSE is **strictly lower**.
- **Classification**: the score is the **accuracy** on the test data (higher is better). The baseline predicts the most frequent training class. `beats` is `True` only if the model's accuracy is **strictly higher**.
- Any other `task`: `ValueError`.
- Return the two scores as plain floats and `beats` as a plain `bool`.

## Example

```text
a linear model on data with a real linear signal      -> (0.51, 2.03, True)
a linear model fitted to pure noise with 20 features   -> (1.31, 1.00, False)     # worse than the mean
```
