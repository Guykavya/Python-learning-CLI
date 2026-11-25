# Pull pieces out of a code

Chapter section 4.4. `str.extract` with **named groups** turns one text column into several columns in one step. A
product code such as `EL-2024-0042` carries three facts: the category, the year, and a running number.

Write `split_product_code(s)`. `s` is a Series of text (values may be missing). Return a DataFrame with **the same index
as `s`** and exactly three columns, in this order:

| column | content | dtype |
|---|---|---|
| `category` | the two capital letters | text |
| `year` | the four digits of the year | `Int64` (nullable integer) |
| `number` | the four-digit number as an integer: `0042` becomes `42` | `Int64` |

Rules:

- Strip spaces at both ends first. Then the **whole** text must be: two capital letters, `-`, four digits, `-`, four
  digits. Lower case (`el-2024-0042`), a short year (`EL-24-0042`) or anything extra does **not** match.
- A value that does not match gives a row of three missing values (never an error, never a half-filled row).
- A missing input gives a row of three missing values.

## Example

```python
import pandas as pd

s = pd.Series(["EL-2024-0042", " HM-2023-0007 ", "el-2024-0042", "EL-24-0042", None, "FD-2025-1234"])
out = split_product_code(s)
print(out.columns.tolist(), [str(d) for d in out.dtypes])
print(out["category"].tolist())
print(out["year"].tolist())
print(out["number"].tolist())
```

```text
['category', 'year', 'number'] ['str', 'Int64', 'Int64']
['EL', 'HM', nan, nan, nan, 'FD']
[2024, 2023, <NA>, <NA>, <NA>, 2025]
[42, 7, <NA>, <NA>, <NA>, 1234]
```
