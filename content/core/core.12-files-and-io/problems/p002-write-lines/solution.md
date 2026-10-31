## Approach

Open with mode `"w"` (it truncates the file), write each line followed by `"\n"`, and return the count. The `with` block closes the file and flushes the data.

## Code

```python
def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    return len(lines)
```

## Complexity

O(total size of the text).

## Another way

Use `print(line, file=f)`. `print` adds the newline for you. Or write `"\n".join(lines) + "\n"` in one call, but then an empty list needs special care.
