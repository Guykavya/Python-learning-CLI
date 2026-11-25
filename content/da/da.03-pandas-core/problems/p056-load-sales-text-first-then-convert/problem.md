# `load_sales`: text first, then convert

Chapter sections 18.2 and 18.3. The safest way to load a messy CSV is to read **every column as text**, so pandas cannot
guess wrongly, and then convert each column on purpose. Write `load_sales(path, money=(), dates=(), bools=(), ints=())`
that returns a pair `(df, losses)`.

1. Read the file with `pd.read_csv(path, dtype="str", encoding="utf-8")`. Columns not named in any of the four
   arguments stay as the text that was read (not stripped or changed).
2. Convert each named column with the rule of its group. Every rule leaves **missing** where it cannot decide; it never
   guesses and never raises:

| group | rule |
|---|---|
| `money` | remove `₹`, `Rs.`, `Rs`, `INR` (any case), commas and spaces, then `to_numeric(errors="coerce")` (a number dtype, such as `Float64`) |
| `dates` | try `%Y-%m-%d`, then `%d/%m/%Y`, then `%b %d, %Y` (first match wins, spaces around are ignored); a datetime column, `NaT` when none matches |
| `bools` | after strip and lower case: `yes`, `y`, `true`, `1` give `True`; `no`, `n`, `false`, `0` give `False`; anything else is missing (`boolean` dtype) |
| `ints` | `to_numeric(errors="coerce")`, a value that is not a whole number (`2.5`, `x`) is missing; dtype `Int64` |

3. `losses` is a dict with one entry for **every converted column**: the number of rows whose raw cell was **not
   missing** (as read by pandas: empty cells and `N/A` are already missing) but whose converted value is missing.

Everything the solution needs (the four converters) is written **inside** your `solution.py`. The row order and the
column order do not change.

## Example

```python
from pathlib import Path

from solution import load_sales

Path("tiny.csv").write_text(
    "id,when,who,price,paid\n1,2025-03-01, asha ,\"₹1,200.50\",Y\n2,02/03/2025,BEN,Rs. 80,no\n3,??,chitra,free,\n",
    encoding="utf-8")
df, losses = load_sales("tiny.csv", money=["price"], dates=["when"], bools=["paid"], ints=["id"])
print(df["price"].tolist(), df["paid"].tolist())
print(df["who"].tolist())
print(losses)
```

```text
[1200.5, 80.0, <NA>] [True, False, <NA>]
[' asha ', 'BEN', 'chitra']
{'price': 1, 'when': 1, 'paid': 0, 'id': 0}
```
