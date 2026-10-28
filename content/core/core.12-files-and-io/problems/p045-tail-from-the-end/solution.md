## Approach

Go backwards in steps. In every step move the position `step` bytes to the left, read exactly those bytes, and put
them **in front of** what you already have. After each step, count the newlines. When there are more than `n`, the
first partial line in `data` is not needed any more, and you have all `n` last lines complete. Splitting at the end is
done on bytes. Only then decode each line, so a multi-byte character cut by a block border is joined again first.

## Code

```python
def tail_lines(path, n=10, block_size=4096):
    if n <= 0:
        return []
    with open(path, "rb") as f:
        f.seek(0, 2)
        pos = f.tell()
        data = b""
        while pos > 0 and data.count(b"\n") <= n:
            step = min(block_size, pos)
            pos -= step
            f.seek(pos)
            data = f.read(step) + data
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    result = []
    for line in lines[-n:]:
        if line.endswith(b"\r"):
            line = line[:-1]
        result.append(line.decode("utf-8"))
    return result
```

## Complexity

Time and memory O(bytes in the last n lines + one block), not O(file size).

## Another way

`collections.deque(f, maxlen=n)` keeps only the last `n` lines while reading the whole file once. It uses little
memory but still reads every byte from the start, so it is slower for huge files.
