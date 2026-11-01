# Single responsibility

A function (or class) should have **one reason to change**. `process_order` in `starter.py`
has four: the input format can change (parsing), the rules can change (validation), the
pricing can change, and the way results are shown can change (printing). Because it also
**prints**, you cannot test it without capturing the screen, and you cannot reuse the checking
in a web page.

Copy `starter.py` to `solution.py` and split the work into these functions (exact names):

| Function | Does | Returns |
|---|---|---|
| `parse_order(text)` | split the text into lines, split each non-blank line on `,`, strip spaces | a list of rows; a row is a list of strings (no judging) |
| `validate_order(rows)` | check each row, **numbered from 1**; one message per bad row | a list of error strings (empty if all fine) |
| `price_order(rows)` | `sum(qty * price)` for **valid** rows, rounded to 2 decimals | a float |
| `process_order(text)` | wire the three together | the string that used to be printed |

Row rules (first failing rule wins): exactly 3 fields; name not empty; quantity a whole number
above 0 (`"3"`, not `"-1"`, `"x"`, `"0"`); price a number that is 0 or more. Messages:

```
row 1: expected 3 fields, found 2
row 2: name is empty
row 3: quantity must be a whole number above 0
row 5: price must be a number, 0 or more
```

`process_order` returns `"OK: 2 lines, total 4.00"` for a valid order, or the error lines
followed by `"INVALID: N problem(s)"`, joined with newlines. **Nothing prints**: no `print` or
`input` anywhere in the file. `process_order` is at most 10 lines, and every function in the
file is at most 15 lines.

**Example**

```python
parse_order("apple, 3, 0.50\n\npear,2,1.25")  # [['apple', '3', '0.50'], ['pear', '2', '1.25']]
validate_order([["fig", "0", "2"]])           # ['row 1: quantity must be a whole number above 0']
price_order([["apple", "3", "0.50"]])         # 1.5
process_order("apple,3,0.50\npear,2,1.25")    # 'OK: 2 lines, total 4.00'
```
