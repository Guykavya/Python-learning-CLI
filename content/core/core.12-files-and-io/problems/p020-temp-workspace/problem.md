# Use a temporary folder and clean up

Write `sort_via_temp(text)` in `solution.py`. It must return a tuple `(lines, path)`:

1. Split `text` into lines with `splitlines()`.
2. Create a **temporary folder** with the `tempfile` module.
3. Write the lines to a file called `work.txt` inside that folder (UTF-8, one line each, with newlines).
4. Read the file back and sort the lines.
5. Return `(sorted_lines, path)`, where `path` is the full path of `work.txt` **as a string**.

When the function returns, the temporary folder and the file must **already be deleted** (the path no longer
exists). Never create files in the current folder.

**Example**

```python
lines, path = sort_via_temp("pear\napple\nfig\n")
lines   # ['apple', 'fig', 'pear']
os.path.exists(path)   # False
```
