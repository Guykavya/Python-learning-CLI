# Types that look alike

Chapter section 2.4. Excel does not enforce a type per column, so one column can mix real numbers, numbers stored as text (`"12"`), blanks, empty strings (`""`, often from a formula) and dates, and look fine. `SUM` skips the text numbers without a warning.

Write `audit_column(ws, col)` for an openpyxl worksheet `ws` and a column letter `col`. Look at the rows **below the header** (row 2 down to `ws.max_row`) and return a dict with these keys:

| key | what it counts |
|---|---|
| `numbers` | `int` or `float` values (a `bool` is **not** a number) |
| `text_numbers` | strings that look like a number after stripping spaces (`"12"`, `" 3.5 "`, `"-7"`) |
| `blanks` | cells whose value is `None` |
| `empty_strings` | cells whose value is `""` |
| `dates` | `datetime.datetime` or `datetime.date` values |
| `other_text` | any other string |
| `booleans` | `True` / `False` |

All values are ints. The seven counts add up to the number of rows below the header.

## Example

A column with `10`, `"12"`, `None`, `""`, a date, `"abc"` and `3.5` gives `numbers = 2`, `text_numbers = 1`, `blanks = 1`, `empty_strings = 1`, `dates = 1`, `other_text = 1`, `booleans = 0`.
