# Groups and groups(): parse a version number

Software versions are often written as three numbers: `major.minor.patch`, sometimes with a
`v` in front. A regex with **three capturing groups** can check the shape and pull out the
three numbers in one step. `m.groups()` then hands you all three as a tuple of strings.

Write `parse_version(s: str) -> tuple[int, int, int] | None` in `solution.py`.

- Ignore spaces (and other whitespace) at the start and end of `s`.
- An optional `v` or `V` may come first.
- Then exactly three runs of digits separated by single dots: `1.2.3`, `10.0.42`.
- Return the three numbers as `int`s. Leading zeros are fine: `01.002.3` gives `(1, 2, 3)`.
- Anything else returns `None`: two or four parts, letters at the end (`1.2.3-beta`),
  a missing number (`1..3`), a sign (`-1.2.3`), an empty string.

**Example**

```python
parse_version("v1.2.3")        # (1, 2, 3)
parse_version("  10.20.30\n")  # (10, 20, 30)
parse_version("1.2")           # None
parse_version("1.2.3.4")       # None
parse_version("v1.2.3-beta")   # None
```
