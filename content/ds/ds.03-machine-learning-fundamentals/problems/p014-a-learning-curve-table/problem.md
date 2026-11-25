# A learning-curve table

Chapter section 7. A **learning curve** shows how the training and validation errors change as the number of training rows grows.

Write `learning_curve_table(make_model, X, y, sizes, val_X, val_y, repeats=30, seed=0)` returning a DataFrame with the columns `n_train, train_rmse, val_rmse, gap`, one row per size, where `gap = val_rmse - train_rmse`:

- use **one** `rng = np.random.default_rng(seed)` for the whole function
- for each `n` in `sizes`, repeat `repeats` times: `idx = rng.choice(len(X), n, replace=False)`, fit `make_model()` on `X[idx], y[idx]`, record the RMSE on those training rows **and** on the fixed validation set
- the row for `n` holds the **means** over the repeats
- `X` and `y` are NumPy arrays; `make_model` is a function with no arguments that returns a fresh unfitted model

## Example

```text
sizes = [12, 20, 40, 80]; make_model = lambda: poly_model(3)
n_train  train_rmse  val_rmse   gap
     12       0.26      0.41   0.15
     80       0.29      0.32   0.03       # train rises, validation falls, the gap closes
```
