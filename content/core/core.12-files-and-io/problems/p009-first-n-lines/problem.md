# Read the first n lines only

Write `first_lines(path, n)` in `solution.py`. It returns a list with the first `n` lines of a UTF-8 text
file, **without** their trailing newline.

- If the file has fewer than `n` lines, return all of them.
- `n = 0` returns `[]`.
- The file may be huge. Do **not** read it all: stop as soon as you have `n` lines.

**Example**

```python
# big.log has 1,000,000 lines: "row 0", "row 1", ...
first_lines("big.log", 2)   # ["row 0", "row 1"]
```
