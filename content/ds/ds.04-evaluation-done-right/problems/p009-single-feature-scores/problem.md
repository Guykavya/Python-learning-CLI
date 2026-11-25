# Single-feature scores

Chapter section 4.2. A feature that **alone** predicts the target almost perfectly is the first suspect for a target leak. Score every column on its own.

Write `single_feature_auc(X, y, cv=5)`. For each column of the DataFrame `X`, compute the mean `cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X[[col]], y, cv=cv, scoring="roc_auc")`. Return a `pandas.Series` indexed by column name, named `"single_feature_auc"`, **sorted from the highest score to the lowest**.

## Example

```text
single_feature_auc(X_churn, y)
retention_offer_sent    0.945     <- far above the rest: ask how it is filled in
contract_month          0.655
support_calls           0.636
...
```
