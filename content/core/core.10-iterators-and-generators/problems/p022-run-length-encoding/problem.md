# Run-length encoding with groupby

Run-length encoding (RLE) is a simple way to compress text with long runs of the same letter.
Old fax machines and simple image formats use it. `"WWWWBBBW"` becomes four `W`, three `B`,
one `W`.

Write two functions in `solution.py`:

- `encode(text)` returns a **list** of tuples `(char, count)`, one for each run of equal
  characters that sit **next to each other**.
- `decode(pairs)` does the opposite: it takes such a list and returns the original string.

Use `itertools.groupby` for `encode`.

**Example**

```python
encode("WWWWBBBW")             # [('W', 4), ('B', 3), ('W', 1)]
encode("")                     # []
decode([("a", 3), ("b", 1)])   # 'aaab'
decode(encode("hello"))        # 'hello'
```

Note: the two `W` runs stay separate. RLE counts runs, not totals.
