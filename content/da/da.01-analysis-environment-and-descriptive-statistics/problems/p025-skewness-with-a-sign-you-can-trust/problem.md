# Skewness with a sign you can trust

Chapter section 14.5. The **population skewness** is the mean of the cubed standardised deviations:

```text
skew = mean( ((x - mean) / sd) ** 3 )      with sd = the POPULATION standard deviation (divide by n)
```

Cubing keeps the sign: a long right tail gives a positive number, a long left tail a negative one, symmetric data about 0.

Write `skewness(values)`. Fewer than 3 values, or zero spread (all values equal), raises `ValueError`. Do not change the caller's list.

## Example

```python
skewness([1, 2, 3, 4, 5])      # 0.0 (symmetric)
skewness([1, 1, 4])            # 0.7071... (a tail to the right)
skewness([-1, -1, -4])         # -0.7071... (the mirror image)
```
