## Approach

Use `Path(folder).iterdir()`, keep the entries that are files and whose lower-cased `suffix` equals the wanted one, collect `.name`, and sort. `iterdir()` returns entries in any order, so sort at the end. `x.txt.bak` has the suffix `.bak`, so it does not match.

## Code

```python
from pathlib import Path


def list_by_suffix(folder, suffix):
    names = []
    for item in Path(folder).iterdir():
        if item.is_file() and item.suffix.lower() == suffix.lower():
            names.append(item.name)
    return sorted(names)
```

## Complexity

O(m log m) for m entries in the folder.

## Another way

`folder.glob("*.txt")` is shorter, but on Linux it is case sensitive, so `a.TXT` would be missed. A loop with `suffix.lower()` is more precise.
