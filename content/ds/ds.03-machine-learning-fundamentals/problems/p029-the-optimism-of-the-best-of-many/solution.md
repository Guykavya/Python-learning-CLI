## Approach

Each candidate is a random linear rule with true accuracy 50%. On 100 validation rows each shows an accuracy of about 50% plus noise of 5 percentage points. The best of 300 is typically 2.5 standard deviations above 50%, about 63%, pure luck. On 1,000 fresh rows the selected rule falls back to about 50%.

## Code

```python
import numpy as np


def best_of_many_optimism(n_models, seed):
    rng = np.random.default_rng(seed)
    X_val = rng.normal(size=(100, 10))
    y_val = rng.integers(0, 2, 100)
    X_test = rng.normal(size=(1000, 10))
    y_test = rng.integers(0, 2, 1000)
    best_acc, best_w = -1.0, None
    for _ in range(n_models):
        w = rng.normal(size=10)
        acc = float(np.mean(((X_val @ w) > 0).astype(int) == y_val))
        if acc > best_acc:
            best_acc, best_w = acc, w
    test_acc = float(np.mean(((X_test @ best_w) > 0).astype(int) == y_test))
    return best_acc, test_acc
```

## Complexity

O(n_models * n).

## Another way

Increase `n_models` and watch the validation score of the winner creep up while the test score stays at 0.5: this is why a final, untouched test set (or nested cross-validation) is needed.
