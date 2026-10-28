## Approach

Use `print(..., file=sys.stderr)` for warnings; plain `print` goes to stdout. `{item!r}` gives the quotes. Look up `sys.stderr` **when the function runs**, not when it is defined, because test tools and programs can replace the stream object. Do not use a default argument like `file=sys.stderr`, which is fixed too early.

## Code

```python
import sys


def sum_numbers(items):
    total = 0
    for item in items:
        try:
            total += int(item)
        except ValueError:
            print(f"warning: skipping {item!r}", file=sys.stderr)
    print(f"total: {total}")
    return total
```

## Complexity

O(n).

## Another way

The `logging` module sends warnings to stderr by default and adds levels and formats. For tiny scripts `print(file=sys.stderr)` is enough.
