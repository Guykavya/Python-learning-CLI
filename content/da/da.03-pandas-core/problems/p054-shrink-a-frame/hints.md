## Hint 1

Go column by column and ask by dtype: integer, float, text, anything else. For integers `pd.to_numeric(..., downcast="integer")` picks the smallest signed type. What is the test for "no value changes" when going from `float64` to `float32`? (Convert, convert back, and compare.)

## Hint 2

```text
for col in df.columns:
    if bool or category:      leave alone
    elif integer dtype:       out[col] = to_numeric(s, downcast="integer")
    elif float dtype:         small = s.astype("float32")
                              if small.astype("float64").equals(s): out[col] = small
    elif text dtype and s.nunique() <= 50:   out[col] = s.astype("category")
```
`Series.equals` treats two `NaN` in the same position as equal, so gaps do not spoil the check. Start from `df.copy()` and write into the copy.
