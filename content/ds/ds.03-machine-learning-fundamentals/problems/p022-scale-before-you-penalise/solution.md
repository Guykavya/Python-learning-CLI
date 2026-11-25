## Approach

Put the scaler before the model inside one pipeline, so that during cross-validation the scaler is refitted on each training fold (no leak), and the penalty treats every feature on the same scale.

## Code

```python
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def ridge_pipeline(alpha):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))
```

## Complexity

Same as a ridge fit plus one pass for the scaler.

## Another way

Scale the data yourself before calling `Ridge`. That works, but it is easy to forget the same scaling for new data, and to leak the test rows into the scaler.
