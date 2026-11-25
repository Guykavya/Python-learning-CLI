## Approach

One `fit`, on train. Two `transform` calls.

## Code

```python
from sklearn.preprocessing import StandardScaler


def scale_split(X_train, X_test):
    scaler = StandardScaler().fit(X_train)
    return scaler.transform(X_train), scaler.transform(X_test)
```

## Complexity

O(n p).

## Another way

Put the scaler inside a `Pipeline`, so that cross-validation refits it on every training fold automatically.
