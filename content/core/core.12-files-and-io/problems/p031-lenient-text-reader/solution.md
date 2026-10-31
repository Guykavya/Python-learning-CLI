## Approach

Use the strict read first, because most files are fine and you want to know when they are not. The decoding error
only appears while reading (not at `open`), so the `f.read()` must be inside the `try`. In the fallback, open the
file again with `errors="replace"`: each undecodable byte becomes one `"\ufffd"`.

## Code

```python
def read_text_lenient(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(), False
    except UnicodeDecodeError:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(), True
```

## Complexity

O(file size). In the bad case the file is read twice.

## Another way

Read the bytes once with `path.read_bytes()` and call `data.decode("utf-8")`. On error, call
`data.decode("utf-8", errors="replace")`. That reads the disk only once.
