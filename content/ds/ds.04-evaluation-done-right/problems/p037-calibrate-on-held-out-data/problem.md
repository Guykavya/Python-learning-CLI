# Calibrate on held-out data

Chapter section 11.4. A model can rank well and still give badly calibrated probabilities (naive Bayes is a classic case). **Calibration** fits a small mapping from the model's scores to probabilities, on data the model was **not** trained on.

In scikit-learn 1.9 the way to calibrate an already-fitted model is to wrap it in `FrozenEstimator` (so it is not refitted) and give it to `CalibratedClassifierCV`:

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
```

(Older tutorials write `CalibratedClassifierCV(model, cv="prefit")`; that option no longer exists.)

Write `calibrate(model, X_train, y_train, X_cal, y_cal)`:

1. fit `model` on the training data;
2. fit `CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")` on the **calibration** data;
3. return the fitted calibrated classifier.

The test set is not an argument: it is used only afterwards, to check the result.

## Example

```text
Gaussian naive Bayes on the churn data:  test ECE 0.19 before, 0.04 after calibration;  AUC almost unchanged
```
