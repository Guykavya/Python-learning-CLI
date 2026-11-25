# The shrinkage path

Chapter section 8. 200 rows, 10 standardised features. The true model uses only `x0`, `x1`, `x2` (coefficients 3, 2, -2); `x3` ... `x9` are junk. Both a ridge and a lasso model were fitted for growing penalty `alpha`; the table shows the coefficients of `x0, x1, x2, x3, x9` (`x3` and `x9` are junk) and how many of the 10 coefficients are **exactly zero**.

```text
RIDGE
  alpha      x0      x1      x2      x3      x9   exact zeros
    0.1   3.104   2.081  -1.936   0.098  -0.050     0
      1   3.091   2.069  -1.927   0.095  -0.047     0
     10   2.965   1.959  -1.841   0.063  -0.028     0
    100   2.107   1.300  -1.278  -0.073   0.054     0
   1000   0.543   0.315  -0.317  -0.063   0.041     0

LASSO
  alpha      x0      x1      x2      x3      x9   exact zeros
   0.01   3.096   2.062  -1.928   0.083  -0.036     0
    0.1   3.006   1.923  -1.851   0.000  -0.000     5
    0.3   2.831   1.699  -1.643   0.000   0.000     7
      1   2.208   0.927  -0.883   0.000   0.000     7
     10   0.000   0.000   0.000   0.000   0.000    10
```

(The tables were produced by running `Ridge(alpha)` and `Lasso(alpha)` from scikit-learn on `StandardScaler`-scaled data, seed 0.)

Write your answer in `answer.md`:

1. What happens to the ridge coefficients as `alpha` grows? Do any reach exactly 0?
2. What happens to the lasso coefficients? What does it do to the junk features `x3` and `x9` already at `alpha = 0.1`?
3. Why does ridge never give an exact zero while lasso does? (Think about the shape of the two penalties near 0.)
4. Why must the features be on the same scale before either penalty is used?
5. Which one would you use to **select features**, and which to **stabilise** a model whose features are correlated?

## After you answer

Compare with the model answer and tick the checklist for the points you made.
