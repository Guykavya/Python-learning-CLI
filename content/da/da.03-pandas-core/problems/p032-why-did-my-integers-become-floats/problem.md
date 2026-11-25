# Why did my integers become floats?

Chapter section 10.2. A column of customer ids was read from a file. Before cleaning it printed as `1, 2, 3`
(`int64`). After one blank cell appeared it prints as `1.0, NaN, 3.0` (`float64`). A teammate asks: "Why did pandas
change my integers? I never asked for floats."

```python
import pandas as pd

print(pd.Series([1, 2, 3]).dtype)                 # int64
print(pd.Series([1, None, 3]).dtype)              # float64
print(pd.Series([1, None, 3], dtype="Int64").tolist())   # [1, <NA>, 3]
```

Explain in `answer.md`, in about 150 to 250 words:

1. **Why** does one missing value turn the integers into floats? (Think about what NumPy can store in an `int64` block.)
2. What does the **nullable** `Int64` dtype change, and what do you pay for it?
3. When in a cleaning script should you convert to `Int64`: before or after the data is clean? Give the reason.

## Example

A start: "A NumPy `int64` column is a block of raw 8-byte integers. Every bit pattern is a valid number, so there is no
spare pattern that could mean *missing*. A float, on the other hand, has a special value for it, `NaN`..."
