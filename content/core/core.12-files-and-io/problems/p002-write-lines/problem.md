# Write a list of lines to a file

Write `write_lines(path, lines)` in `solution.py`.

- `lines` is a list of strings **without** newline characters.
- Write them to `path`, one per line, each ending with `"\n"`, using UTF-8.
- If the file already exists, replace its content.
- Return the number of lines written. An empty list creates an empty file.

**Example**

```python
write_lines("out.txt", ["red", "green"])   # returns 2
# out.txt now contains: "red\ngreen\n"
```
