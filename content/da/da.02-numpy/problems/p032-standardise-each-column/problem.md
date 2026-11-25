# Standardise each column

Chapter sections 11.4–11.5 and 19 (`nptools.zscore`). Write `zscore(x, axis=0, ddof=0)` that standardises `x` along `axis`: subtract the mean and divide by the standard deviation computed along that axis, so that with `axis=0` **every column** ends up with mean 0 and standard deviation 1.

- `x` is an array or nested list of numbers, 1-D or 2-D. Integers are allowed; the result is always `float64` and has the **same shape** as `x`.
- `ddof` is passed to the standard deviation (`0` = population, `1` = sample).
- A **constant** column (standard deviation 0) becomes all zeros, not `nan`, and no RuntimeWarning is raised.
- Do not change the caller's array.

## Example

```python
x = np.array([[1.0, 10.0, 5.0],
              [2.0, 20.0, 5.0],
              [3.0, 30.0, 5.0]])
zscore(x)
# array([[-1.22474487, -1.22474487,  0.        ],
#        [ 0.        ,  0.        ,  0.        ],
#        [ 1.22474487,  1.22474487,  0.        ]])
zscore(x, axis=1)[:, 0]     # each ROW standardised instead
# array([-1.1769647 , -0.88900089, -0.78695176])
```
