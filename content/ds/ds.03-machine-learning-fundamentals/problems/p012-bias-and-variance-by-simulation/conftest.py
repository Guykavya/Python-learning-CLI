import numpy as np
import pandas as pd

def make_curve(n, noise=0.3, seed=0):
    r = np.random.default_rng(seed)
    x = np.sort(r.uniform(0, 1, n))
    return x.reshape(-1, 1), np.sin(2 * np.pi * x) + r.normal(0, noise, n)

import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())
