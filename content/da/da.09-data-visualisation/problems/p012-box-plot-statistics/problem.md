# Box-plot statistics

Chapter section 4.3. A box plot summarises a distribution with five numbers and a rule for outliers:

- `q1`, `median`, `q3`: the quartiles (linear interpolation, as `np.percentile` does by default);
- `iqr = q3 - q1`; the **fences** are `q1 - 1.5 * iqr` and `q3 + 1.5 * iqr`;
- the **whiskers** end at the lowest and highest data value **inside** the fences;
- every value **outside** the fences is an **outlier**.

Write `box_stats(x)` for a list or array of numbers. Return a dict with the keys
`q1`, `median`, `q3`, `whisker_low`, `whisker_high`, `outliers` (a **sorted list** of floats).

```python
box_stats([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
# {'q1': 3.25, 'median': 5.5, 'q3': 7.75, 'whisker_low': 1.0, 'whisker_high': 9.0, 'outliers': [100.0]}
```

## Example

Here `iqr = 4.5`, so the upper fence is `7.75 + 6.75 = 14.5`. The value 100 is above it (an outlier) and the highest value inside the fence is 9.
