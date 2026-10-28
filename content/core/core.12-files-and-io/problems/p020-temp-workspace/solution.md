## Approach

`tempfile.TemporaryDirectory()` is a context manager. It creates a fresh folder with a random name in the system temp area and removes it, with everything inside, when the block ends. Build the path with `Path(folder) / "work.txt"`, write, read back, sort, and return from inside the block; the cleanup still happens. Returning the path afterwards only shows that it is gone.

## Code

```python
import tempfile
from pathlib import Path


def sort_via_temp(text):
    lines = text.splitlines()
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "work.txt"
        with open(path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        with open(path, encoding="utf-8") as f:
            back = [line.rstrip("\n") for line in f]
        return sorted(back), str(path)
```

## Complexity

O(n log n) for the sort.

## Another way

`tempfile.NamedTemporaryFile` makes a single temporary file. `mkdtemp()` makes a folder that you must delete yourself with `shutil.rmtree`. The context manager is the safe choice because you cannot forget the cleanup.
