## Hint 1

Which method learns, and which method only applies what was learned? Which data should each see?

## Hint 2

`s = StandardScaler().fit(X_train)`, then `s.transform(X_train)` and `s.transform(X_test)`.
