## Hint 1

Start with `__init__` and `final_test`, the two methods that decide whether the test set stays sealed. Then add the others one at a time, running each on the diabetes data as you go.

## Hint 2

Sketch of each method:
- `compare`: for each model, `cross_val_score(model, X_dev, y_dev, cv=self.cv, scoring=self.scoring)`; flip the sign for regression
- `learning_curve`: one call to `learning_curve(...)`; build the DataFrame from the fold means
- `tune`: `GridSearchCV(...).fit(X_dev, y_dev)`; return `best_estimator_, best_params_, abs(best_score_)`
- `final_test`: set a flag first, then fit on dev, predict the test set, compute the metrics
