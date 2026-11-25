## Approach

Add up the points. Ties are many (only four possible values), which is fine for AUC (ties count as half).

## Code

```python
import numpy as np


def rule_score(X):
    return (2 * X["contract_month"].to_numpy() + 1 * (X["support_calls"].to_numpy() >= 3)).astype(float)
```

## Complexity

O(n).

## Another way

Fit a depth-2 decision tree on the two columns: it learns a similar rule from data. The hand-made rule is useful precisely because the business already trusts it.
