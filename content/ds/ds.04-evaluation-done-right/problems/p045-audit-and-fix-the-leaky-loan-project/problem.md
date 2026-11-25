# Audit and fix the leaky loan project

Chapter section 15 (the module project). A colleague's loan-default model claims AUC 0.98. Write an **audit** that finds the planted problems in the data and measures the honest performance.

The data (`make_loans`, chapter section 15.1) has one row per loan application with the columns `loan_id`, `customer_id`, `application_day`, `income`, `debt_ratio`, `loan_amount`, `credit_score`, `employment_years`, `birth_year`, `postcode`, `vendor_000 ...`, `collections_calls` and the target `default`.

Write `audit(df)` returning a dict:

| key | how to compute it |
|---|---|
| `"leaky_column"` | the single-feature check: for every column except `loan_id`, `customer_id` and `default`, the mean `cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), df[[col]], df["default"], cv=5, scoring="roc_auc")`; the best column if its score is **above 0.9**, else `None` |
| `"duplicate_rows"` | number of rows whose `loan_id` already appeared (`df.duplicated("loan_id").sum()`) |
| `"group_column"` | among the columns whose name ends in `"_id"`, other than `loan_id`, the first one whose values repeat after removing duplicate loans (several loans per value); `None` if there is none |
| `"leaky_auc"` | the colleague's evaluation: no de-duplication, `FEATS_PLAIN + [leaky_column]` as features, `train_test_split(rows, test_size=0.25, random_state=0)`, `make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))`, test ROC-AUC |
| `"honest_auc"` | drop duplicate loans, never use the leaky column, split with `GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=0)` by the group column, and fit `Pipeline([("pre", ColumnTransformer([("pc", TargetEncoder(random_state=0), ["postcode"])], remainder="passthrough")), ("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=3000))])` on `FEATS_PLAIN + ["postcode"]` (training rows only); test ROC-AUC |

with `FEATS_PLAIN = ["income", "debt_ratio", "loan_amount", "credit_score", "employment_years", "birth_year"]`. The target encoder sits **inside** the pipeline, so it learns from the training rows only.

<details><summary>The data generator <code>make_loans</code> (open after you have tried the audit)</summary>

```python
def make_loans(n=7000, n_customers=700, seed=3, n_vendor=200):
    r = np.random.default_rng(seed)
    cust_effect = r.normal(0, 1.4, n_customers)               # hidden: some borrowers are just riskier
    cust_birth = r.integers(1950, 2003, n_customers)
    cust_post = r.integers(0, 400, n_customers)
    cid = r.integers(0, n_customers, n)
    day = np.sort(r.integers(0, 730, n))
    income = np.exp(r.normal(10.6, 0.5, n)).round(-2)
    debt_ratio = np.clip(r.beta(2.5, 5, n), 0.02, 0.95).round(3)
    amount = np.exp(r.normal(11.2, 0.6, n)).round(-3)
    score = np.clip(r.normal(650, 70, n), 300, 850).round()
    emp = np.clip(r.gamma(2, 3, n), 0, 40).round(1)
    logit = (-3.4 + 3.0 * (debt_ratio - 0.3) - 0.012 * (score - 650) + 0.35 * (amount / income - 1.0)
             - 0.04 * emp + 0.0012 * day + cust_effect[cid])      # default risk drifts upward over time
    default = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    df = pd.DataFrame(dict(loan_id=np.arange(n), customer_id=cid, application_day=day, income=income,
                           debt_ratio=debt_ratio, loan_amount=amount, credit_score=score, employment_years=emp,
                           birth_year=cust_birth[cid], postcode=cust_post[cid]))
    for j in range(n_vendor):
        df[f"vendor_{j:03d}"] = r.normal(size=n)                  # anonymous columns with no signal at all
    df["collections_calls"] = np.where(default == 1, r.poisson(3, n), r.poisson(0.05, n))
    df["default"] = default
    dup = df.sample(frac=0.06, random_state=1)                    # the faulty import loaded 6% of rows twice
    return pd.concat([df, dup], ignore_index=True).sort_values(["application_day", "loan_id"], kind="stable").reset_index(drop=True)
```
</details>

## Example

```text
audit(make_loans(3000, 300, seed=3, n_vendor=20))
-> {"leaky_column": "collections_calls", "duplicate_rows": 180, "group_column": "customer_id",
    "leaky_auc": 0.99, "honest_auc": 0.71}
```
