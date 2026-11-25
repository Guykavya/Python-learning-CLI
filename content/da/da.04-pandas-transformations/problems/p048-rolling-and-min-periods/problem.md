# Rolling and `min_periods`

Chapter section 9.4. A rolling window of size *n* is **trailing** by default: the value at a row uses that row and the
*n − 1* rows before it. Until the window is full the result is `NaN`, unless `min_periods` allows fewer rows.
`center=True` puts the window around the row instead.

```python
import pandas as pd

s = pd.Series([1, 2, 3, 4])
print(s.rolling(2).mean().tolist())
print(s.rolling(2, min_periods=1).mean().tolist())

t = pd.Series([10, 20, 30, 40, 50])
print(t.rolling(3).sum().tolist())
print(t.rolling(3, center=True).sum().tolist())
print(t.rolling(3, center=True, min_periods=1).sum().tolist())
print(int(t.rolling(3, center=True).mean().isna().sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `pd.Series([2, 4, 6]).rolling(2).sum().tolist()` the windows are `[2]` (not full), `[2, 4]` and `[4, 6]`, so the
result is `[nan, 6.0, 10.0]`. The results are floats because a column that can hold `NaN` is float.

## After you answer

- Why is `center=True` fine for a chart but wrong for a forecast?
- With `min_periods=1`, what does the first value of a 7-day average really mean?
