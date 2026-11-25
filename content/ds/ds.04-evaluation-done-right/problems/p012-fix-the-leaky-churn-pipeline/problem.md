# Fix the leaky churn pipeline

Chapter sections 2-4. A colleague's function evaluates a churn model. Open `solution.py` (it contains their code). It has **three** leaks:

1. it **scales** all rows before splitting;
2. it **selects** features on all rows before splitting;
3. it keeps the column `retention_offer_sent`, which is written **after** the customer decides to leave.

Fix `churn_auc(df, seed=0, scaler_cls=StandardScaler)` so that it:

- drops `churned` and `retention_offer_sent` (if present) from the features, and one-hot encodes the rest with `pd.get_dummies(..., dtype=float)`;
- splits **first**: `train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)`;
- fits `make_pipeline(scaler_cls(), SelectKBest(f_classif, k=8), LogisticRegression(max_iter=2000))` on the **training** rows only;
- returns the ROC-AUC on the test rows as a float.

`scaler_cls` is there so the tests can pass in a scaler that records which rows it was fitted on. Use it (call `scaler_cls()`), do not replace it with `StandardScaler()`.

## Example

```text
colleague's version on make_churn(leaks=True):  about 0.97
fixed version:                                  about 0.75-0.78   (the honest number)
```
