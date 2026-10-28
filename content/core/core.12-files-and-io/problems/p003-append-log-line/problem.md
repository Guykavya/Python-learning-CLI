# Append a line to a log file

Write `append_line(path, text)` in `solution.py`.

- Add `text` and a newline at the **end** of the file at `path` (UTF-8).
- Old content must stay.
- If the file does not exist yet, create it.
- Return nothing.

**Example**

```python
append_line("log.txt", "start")
append_line("log.txt", "stop")
# log.txt now contains: "start\nstop\n"
```
