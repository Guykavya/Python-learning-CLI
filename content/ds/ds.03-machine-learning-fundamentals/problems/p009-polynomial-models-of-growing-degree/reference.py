import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())


def fit_errors(degree, X_tr, y_tr, X_val, y_val):
    m = poly_model(degree).fit(X_tr, y_tr)
    train = float(np.sqrt(np.mean((np.asarray(y_tr) - m.predict(X_tr)) ** 2)))
    val = float(np.sqrt(np.mean((np.asarray(y_val) - m.predict(X_val)) ** 2)))
    return train, val
