## Approach

Scan the candidates, keep the one with the smallest validation error. The strict comparison keeps the smaller (simpler) degree when two tie.

## Code

```python
import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())


def best_degree(X_tr, y_tr, X_val, y_val, max_degree=12):
    best, best_v = None, None
    for d in range(1, max_degree + 1):
        m = poly_model(d).fit(X_tr, y_tr)
        v = float(np.sqrt(np.mean((np.asarray(y_val) - m.predict(X_val)) ** 2)))
        if best is None or v < best_v:
            best, best_v = d, v
    return best
```

## Complexity

`max_degree` fits.

## Another way

Cross-validation (section 9) uses several validation sets instead of one, so the choice is less dependent on one lucky split.
