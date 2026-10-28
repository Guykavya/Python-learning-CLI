## Approach

Importing has two halves. First Python must **find** the file: it looks in each folder of `sys.path`,
in order. So we write the file and put its folder at the front of `sys.path`. Then Python **runs** the
file once and keeps the module object in `sys.modules`. A second import of the same name only looks in
`sys.modules` and returns the cached object, so new source is ignored. `importlib.reload` runs the file
again in the same module object.

`importlib.invalidate_caches()` is needed because the finder for a folder remembers the list of files it
saw. A file created a moment ago may not be in that list yet.

## Code

```python
import importlib
import sys
from pathlib import Path


def create_module(folder, name, source):
    path = Path(folder)
    (path / f"{name}.py").write_text(source, encoding="utf-8")
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    importlib.invalidate_caches()
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)
```

## Complexity

O(len(source) + len(sys.path)): writing the file plus the `in` check on the list.

## Another way

`importlib.util.spec_from_file_location(name, path)` can load a file directly from its path without
touching `sys.path`. That is useful for plugins, but then other modules cannot simply `import` it by name.
