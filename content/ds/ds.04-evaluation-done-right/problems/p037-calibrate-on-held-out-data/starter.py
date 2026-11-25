from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator


def calibrate(model, X_train, y_train, X_cal, y_cal):
    """Fit model on train, then a sigmoid calibrator on the calibration data; return the calibrated classifier."""
    raise NotImplementedError
