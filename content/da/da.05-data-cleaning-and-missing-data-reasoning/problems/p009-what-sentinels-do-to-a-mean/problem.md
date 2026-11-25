# What sentinels do to a mean

Chapter section 3.3. Two fake values in a column of eight ages are enough to ruin the mean. Trace what the code
measures before and after `mask` turns the codes into missing values.

```python
import pandas as pd

age = pd.Series([25, 31, -1, 40, 999, 30, 35, 33])
print(round(float(age.mean()), 2), round(float(age.median()), 2))

clean = age.mask(age.isin([-1, 999]))
print(int(clean.isna().sum()), int(clean.count()))
print(round(float(clean.mean()), 2), round(float(clean.median()), 2))
print(clean.tolist())
print(int(age.max()), int(clean.max()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `v = pd.Series([1, 2, 99])`, `print(round(float(v.mean()), 2))` prints `34.0`, and after
`w = v.mask(v == 99)` the line `print(round(float(w.mean()), 2))` prints `1.5`: `mean` skips the missing value.

## After you answer

- Which moved more because of the two codes, the mean or the median? Why is the median "robust"?
- `isna().sum()` and `count()` add up to 8. Why?
- After the codes became missing, why does the list show `25.0` and not `25`?
