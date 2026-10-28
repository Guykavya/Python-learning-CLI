# Count lines, words and characters

Write `count_stats(path)` in `solution.py`. It reads a UTF-8 text file and returns a tuple
`(lines, words, chars)`:

- `lines`: the number of lines (a last line without `\n` still counts).
- `words`: the number of words, where words are separated by any whitespace.
- `chars`: the number of **characters** in the text, including newlines (not bytes).

`path` can be a `str` or a `Path`. An empty file gives `(0, 0, 0)`.

**Example**

If `notes.txt` holds the text `"héllo wörld\nsecond line\n"`:

```python
count_stats("notes.txt")   # (2, 4, 24)
```
