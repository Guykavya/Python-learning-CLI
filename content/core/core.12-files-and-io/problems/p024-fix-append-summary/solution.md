## Approach

Rewrite the function with two `with` blocks. The first reads `src` line by line and counts lines with `"ERROR" in line`. The second opens `dst` in append mode and writes the summary with a newline. Return the count.

## Code

```python
def append_summary(src, dst):
    with open(src, encoding="utf-8") as f:
        count = sum(1 for line in f if "ERROR" in line)
    with open(dst, "a", encoding="utf-8") as out:
        out.write(f"errors={count}\n")
    return count
```

## Complexity

O(n) over the lines of the log; memory O(1) because you loop over the file.

## Another way

Count with `sum(1 for line in f if "ERROR" in line)`. It is shorter and also streams the file.
