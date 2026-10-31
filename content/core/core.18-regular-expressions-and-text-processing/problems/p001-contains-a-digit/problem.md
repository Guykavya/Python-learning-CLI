# Does it contain a digit?

Your first regex function. `re.search(pattern, text)` scans the text from left to right and
returns a **Match object** for the first place where the pattern fits, or `None` if it fits
nowhere. The pattern `\d` means "one digit".

Write `has_digit(s: str) -> bool` in `solution.py`.

- Return `True` if `s` contains at least one digit anywhere, else `False`.
- Use `re.search` with the pattern `r"\d"`.
- Return a real `bool` (`True` / `False`), **not** the Match object and not `None`.

**Example**

```python
has_digit("room 101")     # True
has_digit("no numbers")   # False
has_digit("")             # False
has_digit("version2")     # True
```
