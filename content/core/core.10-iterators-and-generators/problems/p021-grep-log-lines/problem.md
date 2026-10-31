# A small grep for log lines

The command-line tool `grep` prints the lines of a file that contain a word. You will build a
small version for log lines that arrive as a list or a generator of strings.

Write a **generator function** `grep(lines, word, max_count=None)` in `solution.py`. It yields
tuples `(line_number, line)`:

- `line_number` counts **all** lines, starting at 1.
- Only lines that contain `word` are yielded. The match **ignores case**.
- The yielded line has its trailing whitespace (like `"\n"`) removed with `rstrip()`.
- If `max_count` is a number, stop after that many matches. **Do not read any more lines**
  after the last match you need. (Real `grep -m 2` does the same: it stops reading the file.)
  `max_count=None` means no limit.

**Example**

```python
logs = [
    "08:00 INFO start\n",
    "08:01 ERROR disk full\n",
    "08:02 INFO retry\n",
    "08:03 error: network\n",
]
list(grep(logs, "error"))
# [(2, '08:01 ERROR disk full'), (4, '08:03 error: network')]

list(grep(logs, "ERROR", max_count=1))
# [(2, '08:01 ERROR disk full')]          line 3 and 4 are never read
```
