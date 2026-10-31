# Split on many separators

`str.split(",")` splits on one separator. When the input mixes commas, semicolons and
spaces, `re.split(pattern, text)` splits wherever the **pattern** matches.

Write `tokens(s: str) -> list[str]` in `solution.py`.

- Split `s` on any run of separators. A separator is a comma `,`, a semicolon `;`
  or any whitespace (space, tab, newline).
- Several separators in a row count as one split: `"a, ;b"` gives `["a", "b"]`.
- Return no empty strings, even when `s` starts or ends with separators.
- Other characters (hyphens, dots, ...) are part of the tokens.

**Example**

```python
tokens("red, green;blue  yellow")   # ['red', 'green', 'blue', 'yellow']
tokens(" ,a,,b; ")                  # ['a', 'b']
tokens("")                          # []
tokens("x-ray\tv1.2")               # ['x-ray', 'v1.2']
```
