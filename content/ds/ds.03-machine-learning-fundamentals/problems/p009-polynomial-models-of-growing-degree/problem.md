# Polynomial models of growing degree

Chapter section 5. A polynomial of higher degree is more flexible, so it can follow the training points more closely. Whether it also predicts **new** points better is another question.

Use this model (a pipeline: polynomial features, scaling, linear regression):

<details><summary>The data generator and the model (so you can try your function in <code>my-work</code>)</summary>

```python
import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def make_curve(n, noise=0.3, seed=0):
    r = np.random.default_rng(seed)
    x = np.sort(r.uniform(0, 1, n))
    return x.reshape(-1, 1), np.sin(2 * np.pi * x) + r.normal(0, noise, n)


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())
```
</details>

Write `fit_errors(degree, X_tr, y_tr, X_val, y_val)` that fits `poly_model(degree)` on the training data and returns the tuple `(train_rmse, val_rmse)`: the root mean squared error on the training rows and on the validation rows. Define `poly_model` in your `solution.py` as shown (it is not given to you by the tests).

## Example

```text
X_tr, y_tr = make_curve(20, seed=1);  X_val, y_val = make_curve(2000, seed=2)
fit_errors(1, ...)   ->  (0.48, 0.54)      # a line cannot follow a sine
fit_errors(12, ...)  ->  (0.27, 2.44)      # wiggles through the training points, fails on new ones
```
