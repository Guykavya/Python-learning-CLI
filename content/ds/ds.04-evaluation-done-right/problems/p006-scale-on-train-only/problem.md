# Scale on train only

Chapter section 3. A scaler **learns** a mean and a standard deviation, so it must be fitted on the training rows only, then **applied** to both sets.

Write `scale_split(X_train, X_test)` returning `(X_train_scaled, X_test_scaled)` as NumPy arrays: fit one `StandardScaler` on `X_train`, then transform both. Do not modify the inputs.

## Example

```text
X_train = [[1], [2], [3]]     X_test = [[1000000]]
scale_split(X_train, X_test)  ->  ([[-1.22], [0], [1.22]], [[1224742.9]])
```
The giant test value does not change the scaling of the training rows.
