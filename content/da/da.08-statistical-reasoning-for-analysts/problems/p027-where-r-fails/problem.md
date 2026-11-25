# Where r fails

Chapter section 7. Pearson's r only measures straight-line association. Three small cases show where it misleads. You may use a
calculator for square roots.

```python
import numpy as np
from scipy import stats

x = np.arange(-3, 4)
print(f"y = x squared: r = {np.corrcoef(x, x ** 2)[0, 1]:.3f}")

x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 6, 8, 40])
print(f"line plus one far point: Pearson {np.corrcoef(x, y)[0, 1]:.3f}, Spearman {stats.spearmanr(x, y)[0]:.3f}")

y = 2.0 ** x
print(f"doubling curve: Pearson {np.corrcoef(x, y)[0, 1]:.3f}, Spearman {stats.spearmanr(x, y)[0]:.3f}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `x = [1, 2, 3]`, `y = x`, both coefficients are `1.000`.

## After you answer

- Why is r exactly 0 for `y = x^2` although y is a function of x?
- In the second case, which coefficient is moved by the single far point and which is not?
