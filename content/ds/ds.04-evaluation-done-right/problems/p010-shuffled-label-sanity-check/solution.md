## Approach

Breaking the link between features and labels on purpose gives a known answer (0.5). Any procedure that does better on such data is measuring something other than skill.

## Code

```python
import numpy as np


def shuffled_label_check(evaluate, y, repeats=5, seed=0):
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    scores = [float(evaluate(rng.permutation(y))) for _ in range(repeats)]
    return float(np.mean(scores)), float(np.std(scores))
```

## Complexity

`repeats` full evaluations.

## Another way

`sklearn.model_selection.permutation_test_score` does this for an estimator plus a CV scheme and returns a p-value; it cannot catch leaks that happen **before** the estimator (selection on all rows), which is why the whole procedure is passed in here.
