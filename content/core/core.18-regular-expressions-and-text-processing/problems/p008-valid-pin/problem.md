# Quantifier ranges: a valid PIN

`{m,n}` repeats the previous item at least `m` and at most `n` times. `{4}` means exactly four.
Together with `re.fullmatch` it makes length rules easy to state.

Write `valid_pin(s: str) -> bool` in `solution.py`.

- A valid PIN is **4 to 6** digits and nothing else.
- Only the ASCII digits `0`–`9` count. (`\d` also matches digits from other scripts,
  such as the Devanagari `१२३४`. A bank keypad cannot type those, so they are invalid here.)
- No spaces, no signs, no trailing newline.

**Example**

```python
valid_pin("1234")      # True
valid_pin("000000")    # True
valid_pin("123")       # False  (too short)
valid_pin("1234567")   # False  (too long)
valid_pin("12 34")     # False
```
