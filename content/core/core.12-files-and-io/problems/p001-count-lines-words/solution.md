## Approach

Read the whole text once with `encoding="utf-8"`, then count with `splitlines()`, `split()` and `len()`. Because the file is opened in text mode, `len(text)` counts characters, not bytes. `splitlines()` does not make an extra empty line after a final newline.

## Code

```python
def count_stats(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return (len(text.splitlines()), len(text.split()), len(text))
```

## Complexity

O(n) time and memory for a file of n characters.

## Another way

Loop over the file line by line and add up as you go. That uses less memory, which matters for huge files. For a small file the simple version is fine.
