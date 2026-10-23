# read_chunks: iter(callable, sentinel)

Many readers (files, sockets) have a function `read()` that returns the next piece of data and returns an
**empty string** `""` when there is nothing left. That is not an iterator, but `iter(callable, sentinel)`
turns it into one: it calls the callable again and again until the value equals the sentinel.

Write `read_chunks(read)` in `solution.py`. `read` is a function with no arguments. Return the list of all
chunks that `read()` gives **before** the first `""`. Use the two-argument form of `iter`.

**Example**

```python
parts = ["ab", "cd", "e"]
def read():
    return parts.pop(0) if parts else ""

read_chunks(read)    # ["ab", "cd", "e"]
```

`read` must not be called more often than necessary: once per chunk, plus one final call that returns `""`.
