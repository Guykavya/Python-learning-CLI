# Parse a yes/no answer

Write `parse_yes_no(text)` that turns a user's answer into `True` or `False`.

- Ignore case and surrounding spaces.
- `"yes"`, `"y"`, `"true"`, `"1"` mean `True`; `"no"`, `"n"`, `"false"`, `"0"` mean `False`.
- Anything else: raise `ValueError` with exactly this message, where `<text>` is the **original**
  text shown with `repr`:
  `answer must be yes or no (also y/n, true/false, 1/0), got <text>`
- If `text` is not a `str`: raise `TypeError("answer must be text (str), got <type name>")`.

**Examples**

```python
parse_yes_no("Yes")        # True
parse_yes_no("  n ")       # False
parse_yes_no("1")          # True
parse_yes_no("maybe")      # ValueError: answer must be yes or no (also y/n, true/false, 1/0), got 'maybe'
parse_yes_no("")           # ValueError: ... got ''
parse_yes_no(None)         # TypeError: answer must be text (str), got NoneType
```
