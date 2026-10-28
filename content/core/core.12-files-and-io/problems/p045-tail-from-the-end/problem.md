# tail -n: read a file from the end

The last lines of a 10 GB log file are the ones you care about. Reading 10 GB to see 10 lines is silly.
Open the file in **binary** mode, jump to the end with `seek`, and read **blocks backwards** until you have
enough lines.

Write `tail_lines(path, n=10, block_size=4096)` in `solution.py`:

- Return the last `n` lines as a list of `str`, without their line endings (`\n` or `\r\n`).
- If the file has fewer than `n` lines, return all of them. An empty file gives `[]`. `n <= 0` gives `[]`.
- A final newline does not create an extra empty line: `"a\nb\n"` has the lines `["a", "b"]`.
  An empty line in the middle or at the end (`"a\n\n"` gives `["a", ""]`) is a real line.
- Read from the end in blocks of at most `block_size` bytes, and **stop as soon as you have more than `n` newlines**.
  The tests check that a 2 MB file is not read from the start.
- Collect **bytes** and decode them **after** you have the lines (decode as UTF-8). A character that needs several bytes
  can be cut by a block border, so never decode a single block alone.

**Example**

```python
# file content: "one\ntwo\nthree\nfour\n"
tail_lines(path, 2)    # ["three", "four"]
```
