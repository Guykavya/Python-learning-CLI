# Compare semantic versions

Version strings like `"1.10.2"` must compare by **numbers**: `1.10.0` is newer than `1.2.0`, but as text
`"1.10.0" < "1.2.0"`. Build a `Version` class that compares correctly.

Write `Version(text)` in `solution.py`:

- `text` has exactly three parts of digits joined by dots (`"1.10.2"`). Otherwise raise `ValueError`.
- Attributes: `major`, `minor`, `patch` (ints).
- `==`, `<`, `<=`, `>`, `>=` compare `(major, minor, patch)`. Leading zeros are fine: `"1.02.0"` equals `"1.2.0"`.
- Hashable and consistent with `==`.
- `str(v)` is the normalised text (`"1.2.0"`), `repr(v)` is `Version('1.2.0')`.
- Comparing with other types: `==` is `False`; ordering raises `TypeError`.

**Example**

```python
print(Version("1.10.0") > Version("1.2.0"))    # True
print(sorted([Version("2.0.0"), Version("1.10.0"), Version("1.9.3")]))
# [Version('1.9.3'), Version('1.10.0'), Version('2.0.0')]
print(Version("1.02.0") == Version("1.2.0"))   # True
print(max(Version("0.9.9"), Version("0.10.0")))  # 0.10.0
```
