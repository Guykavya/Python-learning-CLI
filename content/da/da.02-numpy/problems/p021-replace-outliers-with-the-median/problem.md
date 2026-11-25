# Replace outliers with the median

Chapter sections 8.3, 8.5 and 14.2 (and da.01's IQR fences). Write `cap_outliers(x, k=1.5)` for a 1-D array of
numbers (at least 2 values, no `nan`). It returns a tuple `(cleaned, n_replaced)`:

1. `q1` and `q3` are the 25th and 75th percentiles with NumPy's **default** method (`"linear"`, which is da.01's
   `"inclusive"` method); `iqr = q3 - q1`.
2. The fences are `q1 - k * iqr` and `q3 + k * iqr`. A value **strictly** below the lower fence or **strictly** above
   the upper fence is an outlier.
3. `cleaned` is a **new** `float64` array, equal to `x` except that every outlier is replaced by the median of `x`
   (the median of **all** values, outliers included).
4. `n_replaced` is the number of outliers, as an int.

The input array is not changed. No Python loops.

## Example

```python
x = np.array([10, 12, 11, 13, 12, 95, 11, -40])
# q1 = 10.75, q3 = 12.25, iqr = 1.5, fences 8.5 and 14.5, median 11.5
cleaned, n = cap_outliers(x)
cleaned.tolist()   # [10.0, 12.0, 11.0, 13.0, 12.0, 11.5, 11.0, 11.5]
n                  # 2
```
