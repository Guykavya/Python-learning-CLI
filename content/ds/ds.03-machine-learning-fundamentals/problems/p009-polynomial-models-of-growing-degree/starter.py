import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def poly_model(degree):
    """PolynomialFeatures(degree) -> StandardScaler -> LinearRegression."""
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())


def fit_errors(degree, X_tr, y_tr, X_val, y_val):
    """(train_rmse, val_rmse) of poly_model(degree) fitted on the training rows."""
    raise NotImplementedError
