# Money stored as text

Chapter sections 12.4 and 18.2. Prices arrive as text in many styles. Write `to_money(s)` that turns a Series of text
into numbers, following these rules:

- Remove the currency marks `₹`, `Rs.`, `Rs` and `INR` (in any letter case), the thousands commas (also the Indian
  `1,23,456` grouping), and spaces around the number.
- The result is numeric (floats). A value that is **not a number after that** becomes missing: `"n/a"`, `"free"`,
  an empty string, and a lone `"-"` (a dash used as "no value").
- A minus sign **in front of digits** is a real negative number (`"-5"` is a refund of 5): keep it.
- Missing input stays missing. The index and order do not change, and the input is not modified.

## Example

```python
import pandas as pd

from solution import to_money

prices = pd.Series(["Rs. 1,250.50", "₹980", " 12,000 ", "n/a", "-", "-5"])
print(to_money(prices).tolist())
```

```text
[1250.5, 980.0, 12000.0, <NA>, <NA>, -5.0]
```
