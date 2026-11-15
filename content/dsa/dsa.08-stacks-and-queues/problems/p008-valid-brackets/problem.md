# Valid brackets

Write `is_valid(text)` that returns `True` if the brackets `()`, `[]` and `{}` in `text` are **balanced**:

- every closer closes the **most recent** opener that is still open, and of the same kind;
- no closer appears when nothing is open;
- at the end nothing is left open.

All other characters (letters, digits, spaces) are ignored. The empty string is valid.

## Example

```python
>>> is_valid("([]{})")
True
>>> is_valid("(]")
False
>>> is_valid("([)]")
False
>>> is_valid("a(b[c]d)e")
True
>>> is_valid("")
True
```

## Constraints

- `0 <= len(text) <= 10**5`.

## Think about

There are exactly **three** ways to be invalid (chapter section 5). Find one short string for each. Which of the three would a counter of open brackets miss?
