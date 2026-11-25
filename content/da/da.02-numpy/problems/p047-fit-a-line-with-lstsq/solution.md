## Approach

Write the line as a matrix equation. With the design matrix `X = [x, 1]` (one row `[x_i, 1]` per point), `X @ [slope, intercept]` is the vector of predictions, and least squares picks the coefficients that minimise the sum of squared differences to `y`. `np.linalg.lstsq` solves exactly that problem (Ch. 16.6).

If every `x` is the same, the column `x` is a multiple of the column of ones: the matrix has rank 1, and infinitely many `(slope, intercept)` pairs fit equally well. `lstsq` does not raise in that case (it returns one of them, the one with the smallest coefficients), so check the returned `rank` yourself.

## Code

```python
import numpy as np


def fit_line(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"x and y have different lengths: {x.size} and {y.size}")
    if x.size < 2:
        raise ValueError(f"need at least 2 points, got {x.size}")
    X = np.column_stack([x, np.ones_like(x)])
    coef, residuals, rank, sing = np.linalg.lstsq(X, y, rcond=None)
    if rank < 2:
        raise ValueError(f"all x values are equal (rank {rank}): a vertical line cannot be written as y = slope * x + intercept")
    slope, intercept = coef
    return float(slope), float(intercept)
```

## Complexity

O(n) for two unknowns (the SVD inside `lstsq` works on an `n × 2` matrix).

## Another way

The closed form for one variable: `slope = sum((x - x̄)(y - ȳ)) / sum((x - x̄)²)` and `intercept = ȳ - slope · x̄`, which also equals `r · std(y) / std(x)` for the slope (Ch. 16.6). The denominator is zero exactly when all `x` are equal, the same failure seen from another side. `np.polyfit(x, y, 1)` does the same fit; `lstsq` generalises to many input columns (multiple regression, ds.02).
