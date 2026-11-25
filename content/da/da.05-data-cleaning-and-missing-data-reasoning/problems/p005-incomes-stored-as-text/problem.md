# Incomes stored as text

Chapter section 3.2. The survey's `income` column is text: `"₹45,200"`, `"Rs. 31000"`, `"N/A"`. The recipe has three
steps: **remove the decoration, turn the codes into missing, convert.** This time the input is messier than in the
chapter, so the rules are written down below. Follow them exactly.

Write `parse_income(s)`. `s` is a Series of text (values may also be missing). Return a Series of **floats** with the
same index. For each value:

1. A missing input gives a missing output.
2. Strip spaces and ignore case. If what is left is `""`, `"n/a"` or `"-999"`, the result is **missing** (these are
   codes that mean "no answer").
3. Remove a **leading** currency mark: `₹`, or `Rs` with an optional dot, followed by any spaces
   (`"₹45,000"`, `"Rs. 31000"`, `"rs 31,000"`).
4. Remove a **trailing** `/-` (`"45000/-"`).
5. If the rest ends with `k`, drop the `k` and multiply the number by 1,000 (`"45k"` is 45000, `"4.5K"` is 4500).
6. Remove commas (so Indian grouping `12,34,567` works).
7. The rest must be digits with an optional decimal part (`45000`, `4.5`). Anything else (`"forty"`, `"-5000"`, `"4.5.6"`,
   a mark with no number) is **missing**. The function never raises an error.

## Example

```python
import pandas as pd

s = pd.Series(["₹45,000", "45k", "Rs. 31000", "45000/-", "forty", "N/A", "4.5K", "12,34,567"])
print(parse_income(s).tolist())
```

```text
[45000.0, 45000.0, 31000.0, 45000.0, nan, nan, 4500.0, 1234567.0]
```

## Why this matters

With `errors="coerce"` a careless parser turns `"1,200"` into `NaN` and throws a good number away. Your function must
keep every amount that a person could read and give up only on text that is not an amount.
