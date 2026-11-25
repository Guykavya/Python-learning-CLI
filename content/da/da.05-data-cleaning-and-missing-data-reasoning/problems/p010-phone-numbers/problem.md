# Phone numbers

Chapter section 4.2. Raw phone numbers come in many styles: `9876543210`, `98765 43210`, `+91-98765-43210`,
`(+91) 9876543210`, `098765-43210`. The plan is **normalise, then validate**: keep only the digits, remove a country
code or trunk zero when what remains is too long, and accept only a valid 10-digit mobile number.

Write `clean_phone(s)`. `s` is a Series of text (values may be missing). Return a Series of text with the same index.
The rules, in this order:

1. Keep **only the digits** of the text (remove everything that is not `0`-`9`).
2. If the digits start with `91` **or** `0` **and exactly 10 digits follow**, remove that prefix (one prefix only).
   Do **not** remove it when something else follows: `9123456789` starts with `91` but only 8 digits follow, so it is a
   real number and stays whole.
3. The result is valid only if it is **exactly 10 digits** and the **first digit is 6, 7, 8 or 9**. A valid result is
   returned as text; anything else becomes **missing**.
4. A missing input gives a missing output. No error is ever raised.

## Cases

| input | output |
|---|---|
| `9876543210` | `9876543210` |
| `98765 43210` | `9876543210` |
| `+91-98765-43210` | `9876543210` |
| `(+91) 9876543210` | `9876543210` |
| `098765-43210` | `9876543210` |
| `919876543210` | `9876543210` |
| `9123456789` | `9123456789` (the `91` is part of the number) |
| `06876543210` | `6876543210` |
| `5876543210` | missing (first digit 5) |
| `91234` | missing (too short) |
| `7874273` | missing (cut off) |
| `0919876543210` | missing (13 digits: `0` is followed by 12 digits, not 10) |
| `00919876543210` | missing (14 digits) |
| `phone: 98765-43210` | `9876543210` |
| empty text, or no digits at all (`n/a`) | missing |

## Example

```python
import pandas as pd

t = pd.Series(["+91 98765 43210", "9123456789", "09876543210", "91234", None, "5876543210"])
print(clean_phone(t).tolist())
```

```text
['9876543210', '9123456789', '9876543210', nan, nan, nan]
```
