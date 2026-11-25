## Hint 1

What are the arguments of `GridSearchCV`, and which attributes hold the best parameters and the best mean score after `fit`?

## Hint 2

`GridSearchCV(model, grid, cv=5, scoring=scoring).fit(X, y)` then `.best_params_` and `.best_score_`.
