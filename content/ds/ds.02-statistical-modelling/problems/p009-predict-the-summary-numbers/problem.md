# Predict the summary numbers

Chapter sections 3 and 5. Five points, one line fitted by least squares. Work out by hand what the program prints.

```python
import numpy as np
import statsmodels.api as sm

x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
y = np.array([2.0, 4.0, 5.0, 4.0, 5.0])
res = sm.OLS(y, sm.add_constant(x)).fit()

print(f"intercept = {res.params[0]:.2f}")
print(f"slope     = {res.params[1]:.2f}")
print(f"R-squared = {res.rsquared:.2f}")
print(f"residual df = {int(res.df_resid)}")
print(f"largest residual = {np.max(np.abs(res.resid)):.2f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `x = [1, 2, 3]` and `y = [2, 4, 6]` the line is exact: the first two lines would be `intercept = 0.00` and `slope     = 2.00`.

## After you answer

- Which point has the largest residual, and is it above or below the line?
