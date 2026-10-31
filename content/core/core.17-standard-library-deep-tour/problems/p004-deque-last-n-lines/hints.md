## Hint 1

`deque(iterable, maxlen=n)` consumes the iterable and keeps only the last `n` items it saw. So the whole of `last_n` can be one constructor call plus a `list(...)`. What does `deque(maxlen=-1)` do? (Try it.)

## Hint 2

An open text file is an iterable of lines, so `last_n(f, n)` works on it directly, one line at a time. Open with `encoding="utf-8"`. In text mode Python turns `\r\n` into `\n` when reading, so after `last_n` you only need to remove a trailing `"\n"` from each line. Why `rstrip("\n")` and not plain `strip()`?

## Hint 3

```
last_n(items, n):
    if n < 0: raise ValueError("n must be >= 0")
    return list(deque(items, maxlen=n))

tail(path, n=10):
    with open(path, encoding="utf-8") as f:
        lines = last_n(f, n)
    return [line.rstrip("\n") for line in lines]
```
