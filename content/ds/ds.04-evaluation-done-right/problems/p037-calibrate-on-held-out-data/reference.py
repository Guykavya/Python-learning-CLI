from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator


def calibrate(model, X_train, y_train, X_cal, y_cal):
    model.fit(X_train, y_train)
    cal = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")
    return cal.fit(X_cal, y_cal)
