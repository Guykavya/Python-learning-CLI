## Approach

First decide **what** to write, then write it. Copy the dict, and for every given path walk up its parent
folders. Each parent except the root (`.`) needs `folder/__init__.py`. `setdefault` adds an empty one only
when the dict does not already have one, so a given `__init__.py` keeps its text. Then write every entry,
creating folders as needed, and return the sorted keys.

Why does it matter? Without `__init__.py`, Python 3 still imports the folder, but as a **namespace
package**: it has no `__file__`, no place for package-level code or `__all__`, and two folders with the
same name on `sys.path` silently merge. For your own code, regular packages are the safe default.

## Code

```python
from pathlib import Path, PurePosixPath


def write_package(root, files):
    all_files = dict(files)
    for rel in files:
        for folder in PurePosixPath(rel).parents:
            if str(folder) == ".":
                continue
            all_files.setdefault(f"{folder}/__init__.py", "")
    for rel, text in all_files.items():
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return sorted(all_files)
```

## Complexity

O(n·d + total text size) for n files of depth d, plus O(m log m) to sort the m written paths.

## Another way

Write the given files first, then walk the tree with `Path(root).rglob("*")`, and for every directory
without `__init__.py` create one with `touch()`. That also catches folders that already existed on disk,
but it is harder to build the return list, and it may touch folders that are not part of this package.
