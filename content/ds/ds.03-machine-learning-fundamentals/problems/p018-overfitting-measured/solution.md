## Approach

The learning curve shows the gap at five sizes. A relative gap above 0.15 says the model overfits; whether more data would cure it depends on whether the gap is still falling (compare the last point with the one at 60% of the data).

## Code

```python
import numpy as np
from sklearn import model_selection


def overfit_report(X, y, model, seed=0):
    sizes, tr, va = model_selection.learning_curve(
        model, X, y, train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0],
        cv=model_selection.KFold(5, shuffle=True, random_state=seed),
        scoring="neg_root_mean_squared_error")
    train = -tr.mean(axis=1)
    val = -va.mean(axis=1)
    gap = val - train
    rel = float(gap[-1] / val[-1])
    high = bool(rel > 0.15)
    helps = bool(high and gap[-1] < gap[2])
    return {"gap": float(gap[-1]), "rel_gap": rel, "high_variance": high, "more_data_helps": helps}
```

## Complexity

`5 x 5` fits.

## Another way

Fit a line through the last three gaps and extrapolate: a negative slope that reaches a small gap within the data you can afford says "collect more".
