# Thousands separators with lookaround

Most regexes match *text*. This one matches **positions**: the gaps between digits where a comma
belongs. A pattern made only of lookarounds is zero-width, and `re.sub` with a zero-width
pattern **inserts** the replacement at each such gap.

Write two functions in `solution.py`. Each must do its work with **one `re.sub` call** on `str(n)`.

1. `commas(n: int) -> str` — Western grouping, a comma every three digits from the right.
2. `commas_indian(n: int) -> str` — Indian grouping: the last three digits form one group,
   and every two digits before that form a group (thousand, lakh, crore).

Both handle `0`, small numbers (no comma) and negative numbers (the `-` stays in front, and no
comma goes right after it).

**Example**

```python
commas(1234567)          # '1,234,567'
commas(-1000)            # '-1,000'
commas(999)              # '999'
commas_indian(1234567)   # '12,34,567'
commas_indian(100000)    # '1,00,000'
commas_indian(-12345)    # '-12,345'
```

Think about it as a question you can ask at every gap between two characters:
*is there a digit just before me, and how many digits are left until the end?*
