# Bias and variance by simulation

Chapter section 6. The error of a model on new data splits into **bias** (it is wrong on average because it is too rigid), **variance** (it changes from one training sample to the next) and noise. Because the truth is known (a sine), you can measure the first two.

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

Write `bias_variance(degree, n_train=30, reps=150, noise=0.3, seed=0)` returning `(bias2, variance)`:

1. `points = np.linspace(0.05, 0.95, 19)`
2. for `r` in `range(reps)`: draw a **fresh training set** with `make_curve(n_train, noise, seed=seed + r)`, fit `poly_model(degree)`, and predict at `points` (shape `(19, 1)`); collect the predictions in an array `P` of shape `(reps, 19)`
3. `bias2 = mean((P.mean(axis=0) - sin(2*pi*points)) ** 2)`
4. `variance = mean(P.var(axis=0))` (population variance, `ddof=0`)

Define `make_curve` and `poly_model` in your file as shown.

## Example

```text
bias_variance(1)   ->  (0.16, 0.02)    # a line: big bias, small variance
bias_variance(3)   ->  (0.003, 0.013)  # about right
bias_variance(9)   ->  (0.01, 0.5)     # flexible: tiny bias, big variance (varies by seed)
```
