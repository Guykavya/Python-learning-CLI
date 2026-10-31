# Character class basics: only hex digits

A **character class** `[...]` matches one character from a set. Ranges save typing:
`[0-9a-f]` is the ten digits plus the letters `a` to `f`. Hexadecimal numbers (used for
colours like `ff8800` and for memory addresses) use exactly these characters, in either case.

Write `only_hex(s: str) -> bool` in `solution.py`.

- Return `True` if `s` is **not empty** and **every** character is a hex digit:
  `0`–`9`, `a`–`f` or `A`–`F`.
- No prefix is allowed: `"0x1F"` is `False` (the `x` is not a hex digit).
- No spaces and no trailing newline: `"ff "` and `"ff\n"` are `False`.

**Example**

```python
only_hex("DEADbeef")   # True
only_hex("12g4")       # False
only_hex("")           # False
only_hex("0x1F")       # False
```
