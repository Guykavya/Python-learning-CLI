# When the z-score hides the outlier

Chapter section 13. Two common outlier rules:

- `flag_iqr(values, k=1.5)`: with the **inclusive** quartiles `q1`, `q3` and `iqr = q3 - q1`, flag a value that is **below `q1 - k * iqr` or above `q3 + k * iqr`** (strictly outside the fences).
- `flag_z(values, t=3)`: with the mean and the **sample** standard deviation, flag a value whose `abs(x - mean) / sd` is **greater than `t`**.

Both return the **indexes** of the flagged values in increasing order. A list with fewer than 2 values, or a constant list (spread 0 for `flag_z`), returns `[]` from `flag_z` and never divides by zero.

The lesson: the z-score uses the mean and the standard deviation, **which the outliers themselves distort**. Two huge values among twelve inflate the standard deviation so much that neither gets a z above 3 (they *mask* each other); the IQR rule still catches them.

## Example

```python
flag_iqr([10, 11, 12, 11, 10, 12, 11, 500])   # [7]
flag_z([10, 11, 12, 11, 10, 12, 11, 500])     # []   (n = 8: a z-score above 3 is impossible here!)
```
