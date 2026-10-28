# Count log levels without read()

A server log can be many gigabytes. `f.read()` and `f.readlines()` would load all of it into memory.
A file object is an **iterator over lines**, so `for line in f` keeps only one line in memory.

Write `count_levels(path)` in `solution.py`. Every log line looks like this:

```text
2024-05-01 10:15:02 ERROR disk almost full
```

date, time, **level**, then a message that may contain any words (also the word `ERROR`).

- Return a dict that maps each level to the number of lines with that level.
- The level is the **third word** of the line.
- A line with fewer than three words (a blank line, a broken line) is skipped.
- Open the file with `open(path, encoding="utf-8")` and loop over it. The tests refuse `f.read()` and `f.readlines()`.
- If the file does not exist, let `FileNotFoundError` go up (do not catch it).

**Example**

```text
2024-05-01 10:15:02 INFO started
2024-05-01 10:15:03 ERROR disk full: ERROR 28
broken line

2024-05-01 10:15:04 INFO stopped
```

`count_levels(path)` returns `{"INFO": 2, "ERROR": 1}`.
