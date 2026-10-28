# A custom format spec with __format__

In `f"{x:>8}"` the part after the colon is the **format spec**. Python passes it to
`x.__format__(spec)`, so your own class can define its own spec language.

Write a class `Color` in `solution.py`:

- `Color(r, g, b)` stores three ints from 0 to 255.
- `repr(c)` is `Color(255, 128, 0)`.
- `format(c, spec)` (and `f"{c:spec}"`) works like this:
  - `""` (empty spec): the same as `str(c)`. Since you do not define `__str__`, that is the repr.
  - `"hex"`: `#ff8000` (lowercase, two digits per channel)
  - `"rgb"`: `rgb(255, 128, 0)`
  - anything else: raise `ValueError` with a message that contains the bad spec.

**Example**

```python
c = Color(255, 128, 0)
print(f"{c:hex}")    # #ff8000
print(f"{c:rgb}")    # rgb(255, 128, 0)
print(f"{c}")        # Color(255, 128, 0)
format(c, "xyz")     # ValueError
```
