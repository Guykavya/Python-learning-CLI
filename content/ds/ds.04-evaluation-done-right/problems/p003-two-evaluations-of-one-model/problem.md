# Two evaluations of one model

Chapter section 1.2. Score the **same model** twice: once with all columns and once without one suspicious column. If removing a single column costs a huge amount of AUC, that column deserves a question: *when is it filled in?*

Write `two_evaluations(X, y, model, suspect)` returning `(auc_with, auc_without)`: the mean 5-fold cross-validated ROC-AUC of `model` on all columns of `X`, and on `X` without the column `suspect`. Use `StratifiedKFold(5, shuffle=True, random_state=0)` and `scoring="roc_auc"` (this is the chapter's `cv_auc`). Raise `KeyError` if `suspect` is not a column.

<details><summary>The data generator <code>make_churn</code> (chapter section 1.1)</summary>

```python
def make_churn(n=4000, seed=0, leaks=False):
    """Synthetic telecom customers. The true churn rule is known and noisy."""
    r = np.random.default_rng(seed)
    contract = r.choice(["month", "year", "two_year"], n, p=[.55, .25, .20])
    tenure = np.clip(r.gamma(2.2, 12, n), 1, 72).round()
    charge = np.clip(r.normal(65, 22, n), 20, 120).round(2)
    calls = r.poisson(1.2 + 0.03 * (charge - 65) / 10 + 0.6 * (contract == "month"), n)
    autopay = r.random(n) < 0.5
    region = r.choice(["north", "south", "east", "west"], n)
    logit = (-1.6 + 1.1 * (contract == "month") - 0.9 * (contract == "two_year")
             - 0.025 * tenure + 0.018 * (charge - 65) + 0.38 * calls - 0.5 * autopay)
    churn = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    df = pd.DataFrame(dict(tenure_months=tenure, monthly_charge=charge, support_calls=calls,
                           contract=contract, autopay=autopay.astype(int), region=region,
                           churned=churn))
    if leaks:
        # Written AFTER the customer decided: 92% of churners got an offer, only 4% of stayers.
        df["retention_offer_sent"] = np.where(churn == 1, r.random(n) < 0.92,
                                              r.random(n) < 0.04).astype(int)
    return df
```
</details>

## Example

```text
churn = make_churn(leaks=True); X = pd.get_dummies(churn.drop(columns="churned"), dtype=float)
two_evaluations(X, churn["churned"], logistic_pipeline, "retention_offer_sent")  ->  (0.968, 0.759)
```
