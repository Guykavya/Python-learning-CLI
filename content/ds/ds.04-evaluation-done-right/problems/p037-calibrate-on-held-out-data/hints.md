## Hint 1

Why must the calibration data be different from the training data? What would the calibrator learn from the training rows, which the model already fits too well?

## Hint 2

```text
model.fit(X_train, y_train)
cal = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid").fit(X_cal, y_cal)
return cal
```
