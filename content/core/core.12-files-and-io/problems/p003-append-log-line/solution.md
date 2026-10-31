## Approach

Mode `"a"` opens for appending: the write position is always the end, old content stays, and a missing file is created. Write the text plus `"\n"` and let `with` close the file.

## Code

```python
def append_line(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")
```

## Complexity

O(len(text)) per call, no matter how big the file is.

## Another way

Mode `"x"` creates a file and fails if it exists. Mode `"r+"` needs `seek(0, 2)` first. Plain `"a"` is the right tool for logs.
