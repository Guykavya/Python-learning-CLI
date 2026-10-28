# A statistics summary

The `statistics` module has well-tested versions of the formulas you might be tempted to write
yourself. Use it.

1. `summary(data) -> dict` with exactly these keys:

   | key | value |
   |---|---|
   | `"count"` | number of values |
   | `"mean"` | arithmetic mean (`statistics.fmean` or `statistics.mean`) |
   | `"median"` | the middle value (average of the two middle ones for an even count) |
   | `"modes"` | a **list** of the most common values, in first-seen order (`statistics.multimode`) |
   | `"stdev"` | **sample** standard deviation; `None` if there is only one value |
   | `"pstdev"` | **population** standard deviation |
   | `"range"` | `max - min` |

   An empty list raises `ValueError`.

2. `quartiles(data) -> list[float]`: `[Q1, Q2, Q3]` from `statistics.quantiles(data, n=4)`,
   with its default method.

3. `outliers(data) -> list[float]`: the values below `Q1 - 1.5 * IQR` or above `Q3 + 1.5 * IQR`
   (where `IQR = Q3 - Q1`), in their original order. This is the usual "box plot" rule.

Do not change the caller's list.

**Example**

```python
summary([2, 4, 4, 4, 5, 5, 7, 9])
# {'count': 8, 'mean': 5.0, 'median': 4.5, 'modes': [4],
#  'stdev': 2.138089935299395, 'pstdev': 2.0, 'range': 7}
quartiles([1, 2, 3, 4, 5, 6, 7, 8])                 # [2.25, 4.5, 6.75]
outliers([10, 12, 11, 13, 12, 11, 95, 12, -40])     # [95, -40]
```
