## Approach

Compare the **before** and the **after**. A value was lost when the result is missing but the input was neither missing nor empty. Strip the spaces first so that padding is not mistaken for bad data, and report the stripped text, which is what you would show a data owner. `unique()` and `sorted` make the list short and stable.

## Code

```python
import pandas as pd


def convert_numbers(s):
    text = s.str.strip()
    numbers = pd.to_numeric(text, errors="coerce").astype("float64")
    lost = numbers.isna() & text.notna() & (text != "")
    bad_values = sorted(text[lost].unique().tolist())
    return numbers, bad_values
```

## Complexity

O(n) plus O(k log k) to sort k distinct bad values.

## Another way

`pd.to_numeric(text)` without `coerce` raises on the first bad value and names it, but only that one. Counting the lost values in a loop is slower and no clearer. The same before/after comparison is the basis of the conversion log in Ch. 18 and of problem 57.
