# List the files with a given suffix

Write `list_by_suffix(folder, suffix)` in `solution.py`. It returns a **sorted list of file names**
(strings, not full paths) of the files directly inside `folder` whose suffix is `suffix`.

- `suffix` looks like `".txt"`. Compare ignoring case: `.TXT` matches `.txt`.
- Only **files**. A folder named `data.txt` must not be listed.
- Do not look inside sub-folders.
- `folder` may be a `str` or a `Path`.

**Example**

```python
# folder has: b.txt, a.TXT, c.csv, notes (a folder), x.txt.bak
list_by_suffix(folder, ".txt")   # ["a.TXT", "b.txt"]
```
