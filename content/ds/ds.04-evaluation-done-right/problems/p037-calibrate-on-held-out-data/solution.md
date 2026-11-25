## Approach

Train the model, freeze it, and learn the score-to-probability map on a separate set. Three parts of the data: training, calibration, test.

## Code

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator


def calibrate(model, X_train, y_train, X_cal, y_cal):
    model.fit(X_train, y_train)
    cal = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")
    return cal.fit(X_cal, y_cal)
```

## Complexity

One model fit and one small logistic fit.

## Another way

`CalibratedClassifierCV(model, cv=5)` fits and calibrates with internal cross-validation on the training data; it averages five calibrated copies. `method="isotonic"` is more flexible but needs more calibration rows.
