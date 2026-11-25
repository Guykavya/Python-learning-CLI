import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())


def best_degree(X_tr, y_tr, X_val, y_val, max_degree=12):
    """Degree 1..max_degree with the lowest validation RMSE (smaller degree on a tie)."""
    raise NotImplementedError
