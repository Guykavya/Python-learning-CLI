# All the numbers in a sentence

`re.findall(pattern, text)` returns **every** non-overlapping match as a list of strings.
That makes "pull all the numbers out of this text" a one-liner.

Write `numbers(s: str) -> list[int]` in `solution.py`.

- Find every whole number (a run of digits `0`–`9`) in `s`, in order, and return them as `int`s.
- A minus sign **directly** before the digits makes the number negative: `-3` is `-3`.
  A minus with a space after it (`- 3`) is not a sign, so that gives `3`.
- Only integers: a dot is just a separator, so `3.14` gives `3` and `14`.
- `"10-3"` gives `[10, -3]` (the minus is directly before `3`). This is a deliberate, simple rule.
- No numbers: return `[]`.

**Example**

```python
numbers("Room 101, floor -2, 3 lifts")   # [101, -2, 3]
numbers("pi is about 3.14")              # [3, 14]
numbers("no digits here")                # []
numbers("007 agents")                    # [7]
```
