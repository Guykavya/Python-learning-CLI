## Hint 1

Read the function from top to bottom and mark every line that learns something (a fit). Which rows does each one see?

## Hint 2

```text
X = get_dummies(df.drop(columns=["churned", "retention_offer_sent"] that exist), dtype=float); y = df["churned"]
Xa, Xb, ya, yb = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
pipe = make_pipeline(scaler_cls(), SelectKBest(f_classif, k=8), LogisticRegression(max_iter=2000)).fit(Xa, ya)
return roc_auc_score(yb, pipe.predict_proba(Xb)[:, 1])
```
