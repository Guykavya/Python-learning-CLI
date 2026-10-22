# safe_int: parse or None

Write three annotated functions in `solution.py`.

1. `safe_int(text: str) -> int | None`: turn text into an `int`. Spaces around the number are
   allowed. If the text is not a whole number (empty, letters, a decimal like `"4.5"`), return
   `None` instead of raising.
2. `safe_int_or(text: str, default: int) -> int`: the same, but return `default` when the text is
   not a whole number. Never returns `None`.
3. `parse_all(texts: list[str]) -> list[int]`: parse every text with `safe_int` and keep only the
   ones that worked, in the original order.

The hints are part of the tests.

**Examples**

```python
safe_int("42")            # 42
safe_int(" -7 ")          # -7
safe_int("abc")           # None
safe_int("4.5")           # None
safe_int_or("x", 0)       # 0
safe_int_or("0", 5)       # 0
parse_all(["1", "x", "3", ""])   # [1, 3]
```
