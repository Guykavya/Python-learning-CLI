## Hint 1

Do the checks one by one and test each on the data before moving on. The single-feature check is the slowest part; restrict it to the columns described.

## Hint 2

```text
leak = best single-feature AUC column if > 0.9
dups = df.duplicated("loan_id").sum()
u = df.drop_duplicates("loan_id"); group = first "_id" column (not loan_id) with u[col].nunique() < len(u)
leaky_auc: random row split on df with FEATS_PLAIN + [leak]
honest_auc: GroupShuffleSplit on u by group; pipeline with TargetEncoder(postcode) + scaler + logistic regression
```
