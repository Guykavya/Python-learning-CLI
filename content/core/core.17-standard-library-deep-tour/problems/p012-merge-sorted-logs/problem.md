# heapq.merge: merge sorted log files lazily

Three servers each write a log file, and each file is already in time order. You want one
combined log in time order. Reading all files into one list and sorting it works, until the
logs are 30 GB. `heapq.merge(*iterables, key=...)` merges **already sorted** inputs
**lazily**: it holds only one pending line per input and yields the next smallest each time.

Every log line starts with a 19-character timestamp, then a space and the message:

```text
2025-03-01T10:00:05 web1 GET /
```

Write two functions in `solution.py`.

1. `merge_logs(*sources: Iterable[str]) -> Iterator[str]`
   - Each source is an iterable of lines, sorted by timestamp. Return an **iterator** over all
     lines in timestamp order. Lines are passed through unchanged.
   - Order by the **timestamp only** (`line[:19]`). When two lines have the same timestamp, the
     one from the **earlier source** (earlier argument) comes first; within one source, keep its order.
   - It must be lazy: do not read a source further than needed.
2. `merge_files(paths: list[Path], out_path: Path) -> int`
   - Open every file (UTF-8), merge them with `merge_logs`, and write the merged lines to
     `out_path`, one per line, each ending with `"\n"`. Skip blank lines.
   - The last line of an input file may have no newline; it must not get glued to the next line.
   - Return the number of lines written.

**Example**

```python
a = ["2025-03-01T10:00:00 a1", "2025-03-01T10:00:05 a2"]
b = ["2025-03-01T10:00:01 b1", "2025-03-01T10:00:05 b2"]
list(merge_logs(a, b))
# ['2025-03-01T10:00:00 a1', '2025-03-01T10:00:01 b1',
#  '2025-03-01T10:00:05 a2', '2025-03-01T10:00:05 b2']
```
