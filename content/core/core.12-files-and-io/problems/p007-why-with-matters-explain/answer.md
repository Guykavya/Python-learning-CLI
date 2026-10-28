**1. Buffering.** Writing to disk is slow, so Python collects the text in a buffer in memory. `write()` only
puts the text in that buffer. The data goes to the operating system when the buffer is full, when you call
`flush()`, or when the file is closed.

**2. Lost data.** If the file is never closed and the program is killed or crashes hard, the last part of the
buffer never reaches the disk. The file can be empty or cut off in the middle of a line. In CPython the
object is often closed when it is garbage collected, but you cannot count on that, and it does not happen
after a hard crash.

**3. What `with` does.** When the block ends, `with` calls `close()`, which flushes the buffer and releases the
file. It does this after the last line of the block and also when an exception leaves the block, so the
data written so far is saved and the error still continues upward.

**4. Other problems.** Every open file uses an operating system handle. A loop that opens thousands of files
without closing them hits the limit ("too many open files"). A file that is still open can also be locked, so
other programs (or Windows itself) cannot delete, move or read it.

**5. Fixed code.**

```python
def save_scores(path, scores):
    with open(path, "w", encoding="utf-8") as f:
        for s in scores:
            f.write(f"{s}\n")
```
