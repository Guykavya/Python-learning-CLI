# Find the sweet spot

Chapter section 5. Training error always falls with flexibility, so you cannot choose the model by it. Choose by **validation** error.

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

Write `best_degree(X_tr, y_tr, X_val, y_val, max_degree=12)`. For every degree `1 .. max_degree` fit `poly_model(degree)` (define it in your file as shown) on the training rows, compute the RMSE on the validation rows, and return the degree with the **lowest** validation RMSE (on a tie, the smaller degree).

## Example

```text
X_tr, y_tr = make_curve(100, seed=1);  X_val, y_val = make_curve(2000, seed=101)
best_degree(X_tr, y_tr, X_val, y_val)   ->  between 3 and 6    # the truth is a sine wave
```
