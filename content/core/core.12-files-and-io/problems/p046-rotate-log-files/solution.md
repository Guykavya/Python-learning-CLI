## Approach

Always move the **oldest** file first. The oldest slot is cleared by deleting it; then each file moves into a slot that has
just become free. Going from `keep-1` down to `1` means every target is free when we use it. Last, the live file
moves to `.1`. `os.replace` is used for each move, so it works also when the target exists on Windows.

## Code

```python
import os
from pathlib import Path


def rotate_logs(path, keep=3):
    if keep < 1:
        raise ValueError("keep must be at least 1")
    path = Path(path)

    def numbered(i):
        return path.with_name(f"{path.name}.{i}")

    numbered(keep).unlink(missing_ok=True)
    for i in range(keep - 1, 0, -1):
        if numbered(i).exists():
            os.replace(numbered(i), numbered(i + 1))
    if path.exists():
        os.replace(path, numbered(1))


def append_log(path, line, max_bytes=1000, keep=3):
    path = Path(path)
    text = line + "\n"
    size = path.stat().st_size if path.exists() else 0
    if size + len(text.encode("utf-8")) > max_bytes:
        rotate_logs(path, keep)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(text)
```

## Complexity

`rotate_logs` does O(keep) file operations. `append_log` is O(1) apart from that.

## Another way

Use `glob` to find all `path.*` files, sort them by their number, and move them in reverse order. That also handles a
`keep` that was lowered later, by deleting every file above the new limit.
